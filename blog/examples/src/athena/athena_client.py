import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum, unique
from logging import Logger
from typing import Any, Dict, List, Optional

from botocore.exceptions import ClientError
from mypy_boto3_athena.client import AthenaClient as AthenaSdkClient
from typing_extensions import TypeAlias

AthenaQueryResult: TypeAlias = List[Dict[str, Any]]


class QueryExecutionFailed(Exception):
    pass


@unique
class AthenaQueryStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class AthenaClientConfig:
    s3_output_location: str
    query_waiting_delay: float = 0.25  # second
    timeout: int = 600  # seconds
    maximum_workers_number: Optional[int] = None


@dataclass
class AthenaQuery:
    database_name: str
    sql_statement: str
    result: AthenaQueryResult = field(default_factory=lambda: [])
    status: AthenaQueryStatus = AthenaQueryStatus.QUEUED

    def __post_init__(self) -> None:
        if not self.database_name:
            raise ValueError("`database_name` may not be empty!")

    @property
    def is_successful(self) -> bool:
        return bool(self)

    def __bool__(self) -> bool:
        return self.status == AthenaQueryStatus.SUCCEEDED


class AthenaClient:
    def __init__(
        self,
        sdk: AthenaSdkClient,
        config: AthenaClientConfig,
        logger: Logger,
    ) -> None:
        self._sdk = sdk
        self._config = config
        self._logger = logger

    def execute(self, query: AthenaQuery) -> None:
        self._logger.info(
            "Running query `%s` on `%s`",
            query.sql_statement,
            query.database_name,
        )
        try:
            query.result = self._execute(query.sql_statement, query.database_name)
            query.status = AthenaQueryStatus.SUCCEEDED
        except QueryExecutionFailed:
            query.status = AthenaQueryStatus.FAILED

    def execute_many(self, *queries: AthenaQuery) -> None:
        self._logger.info(
            "Running `%s` queries in parallel",
            len(queries),
        )

        max_workers = self._config.maximum_workers_number or len(queries)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for query in queries:
                future = executor.submit(self._execute, query.sql_statement, query.database_name)
                futures[future] = query

            for future in as_completed(futures):
                query = futures[future]

                if future.exception():
                    query.status = AthenaQueryStatus.FAILED
                else:
                    query.result = future.result()
                    query.status = AthenaQueryStatus.SUCCEEDED

    def _execute(self, sql_statement: str, database_name: str) -> AthenaQueryResult:
        response = self._sdk.start_query_execution(
            QueryString=sql_statement,
            QueryExecutionContext={"Database": database_name},
            ResultConfiguration={"OutputLocation": self._config.s3_output_location},
        )
        query_execution_id = response["QueryExecutionId"]
        self._logger.info("query_execution_id = `%s`", query_execution_id)
        self._wait_for_query_results(query_execution_id)
        return self._get_query_results(query_execution_id, is_describe_query="DESCRIBE" in sql_statement)

    def _wait_for_query_results(self, query_execution_id: str) -> None:
        self._logger.info("Waiting for query_execution_id = `%s` to finish", query_execution_id)

        start_time = time.time()
        while True:
            try:
                response = self._sdk.get_query_execution(QueryExecutionId=query_execution_id)
                state = response["QueryExecution"]["Status"]["State"]
                valid_statuses = [
                    str(AthenaQueryStatus.SUCCEEDED),
                    str(AthenaQueryStatus.FAILED),
                    str(AthenaQueryStatus.CANCELLED),
                ]
                if state in valid_statuses:
                    return

                if time.time() - start_time > self._config.timeout:
                    self._logger.error(
                        "Query `%s` execution reached out the maximum timeout value (%s).",
                        query_execution_id,
                        f"{self._config.timeout}s",
                    )
                    raise QueryExecutionFailed(f"Query `{query_execution_id}` execution timeout has been reached")

                self._logger.info(
                    "Waiting %s before next check on query status.",
                    f"{self._config.query_waiting_delay}s",
                )
                time.sleep(self._config.query_waiting_delay)
            except ClientError as error:
                self._logger.error(
                    "An unexpected error occurred. Error = %s",
                    str(error),
                )
                raise QueryExecutionFailed("An unexpected error occurred during query execution") from error

    def _get_query_results(self, query_execution_id: str, is_describe_query: bool = False) -> AthenaQueryResult:
        try:
            self._logger.info("Getting query results for %s", query_execution_id)
            response = self._sdk.get_query_execution(QueryExecutionId=query_execution_id)
            state = response["QueryExecution"]["Status"]["State"]

            if state != str(AthenaQueryStatus.SUCCEEDED):
                self._logger.info(
                    "Query `%s` has finished with a state = %s",
                    query_execution_id,
                    state,
                )
                raise QueryExecutionFailed(f"Query `{query_execution_id}` has finished with a not-success state.")

            results_paginator = self._sdk.get_paginator("get_query_results")
            results_iterator = results_paginator.paginate(
                QueryExecutionId=query_execution_id,
                PaginationConfig={"PageSize": 1000},
            )
            results = []
            columns = None
            for results_page in results_iterator:
                if not columns:
                    columns = [col["Label"] for col in results_page["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]

                for row in results_page["ResultSet"]["Rows"]:
                    values = [item.get("VarCharValue") for item in row["Data"]]
                    results.append(dict(zip(columns, values)))

            # remove items that contains column name as the item value, Athena always returns column names as the first
            # item inside ["ResultSet"]["Rows"], because we are using paginator, this will happen on every page.
            filtered_list = [
                item for item in results if not any(column in item.values() for column in columns)  # type: ignore
            ]

            if is_describe_query:
                describe_query_response = []
                for row in filtered_list:  # type: ignore
                    cleaned_column_name = row["col_name"].split("\t")[0].strip()  # type: ignore
                    cleaned_column_value = row["col_name"].split("\t")[1].strip()  # type: ignore

                    if cleaned_column_name and not cleaned_column_name.startswith("#"):
                        describe_query_response.append({cleaned_column_name: cleaned_column_value})

                return describe_query_response

            return filtered_list
        except ClientError as error:
            self._logger.error(
                "An unexpected error occurred. Error = %s",
                str(error),
            )
            raise QueryExecutionFailed("An unexpected error occurred during query execution") from error
