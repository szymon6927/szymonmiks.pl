+++
author = "Szymon Miks"
title = "Enhancing AWS Athena Efficiency - Building a Python Athena Client"
description = "Tired of wrestling with AWS Athena for your data needs? Join me as I had the same - the results of this journey are described in this blog post."
date = "2023-10-30"
image = "img/1_lhAIRhZwMOuOiYccFMfWQw.png"
categories = [
     "Python", "Software_Development", "AWS"
]
tags = [
    "python",
    "software development",
    "AWS",
    "AWS Athena",
    "python athena client",
    "athena custom wrapper"
]
draft = false
+++

## Intro

So, a while back, as part of my work-related escapades,
I was assigned to a ticket that was about running a few quite complex SQL queries in AWS Athena.

So, I moved the ticket to "in progress" and started working on it.
When I opened [boto3 Athena documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/athena.html)
my first thought was "Ohh, it will be a tough journey" :smile:


## What is AWS Athena?

For those unfamiliar, Athena is Amazon's serverless query service that lets you analyze data in S3 using standard SQL.
Athena offers the power of SQL queries on data stored in S3.

If you have not heard about AWS Athena, I encourage you to take a look at this service.
You can read more about it [here](https://aws.amazon.com/athena/).


## The problem with Athena

Managing Athena queries is a formidable task especially when you're dealing with a heap of queries (that was my case).

Those who have ever worked with AWS Athena know what I'm talking about :wink:.

In a nutshell, the whole process looks as follows:
- you run the query
- as a result of the above, you get the query execution id
- if the query state value is "successful" you can fetch the query result
- if it is succeeded you can fetch the query result

About the above, let me highlight the most problematic things, at least from my perspective:
- you have to monitor query states, you have to ensure they are completed successfully
- you have to monitor query execution time (it demands constant vigilance)
- you have to handle result pagination (by default Athena returns only the first 1000 records)
- you have to take care of error management
- Athena returns `describe <table>` statement result as plain text

I'm highlighting it because when I saw the ticket at the beginning
I was almost sure that it would be as simple as running any SQL statement in some SQL database.

That's why I decided to write a custom Python Athena client, that will solve all of these problems.

The goal was simple: **a nice and stable interface that would hide all the Athena’s meanders.**

## Implementation

The requirements are as follows:
- I want to be able to execute a single query in AWS Athena
- I want to be able to execute multiple queries in AWS Athena at once (as it is a serverless service, and it scales very well)
- I want to have query results as a list of dicts
- I don't want to cast the column values, everything is returned as a string even if a column type is, for example, timestamp, or integer

Check the code below :rocket:

```python
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

            # remove items that contains column name as the item value,
            # Athena always returns column names as the first
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

```

**`execute`** function is responsible for executing a single query in Athena. The query is represented by the `AthenaQuery` object.
If the execution is successful, it sets the `query.status` to `AthenaQueryStatus.SUCCEEDED` and stores the query results in `query.result`.
If the query execution fails, it sets the `query.status` to `AthenaQueryStatus.FAILED`.

**`execute_many`** function is responsible for executing multiple queries in Athena concurrently.
It determines the number of threads to use based on the maximum_workers_number configuration or the total number of queries if no maximum_workers_number is specified.
It uses a ThreadPoolExecutor to manage the concurrent execution of queries.
For each query, it submits a task to the thread pool.
As tasks are completed, it updates the status and result of each query based on the task's outcome.
If a task fails, the query's status is set to `AthenaQueryStatus.FAILED`, and if it succeeds, the status is set to `AthenaQueryStatus.SUCCEEDED`, and the result is stored in `query.result`.

These functions execute queries in Athena either individually or in parallel,
providing you with the flexibility to process multiple queries concurrently while managing their statuses and results.
The use of a thread pool ensures that tasks are executed safely in separate threads without interfering with each other.

If you want to check the tests, they are available on my GitHub [here](https://github.com/szymon6927/szymonmiks.pl/blob/master/blog/examples/tests/test_athena/test_athena_client.py#L65) :wink:

## Usage

I want to show you a real case from my project where I applied my Athena client.
I will anonymize the business domain to not break the NDA but the logic stays the same.

Let's imagine that you have a list of string values, and for these values, you have to generate all combinations.
Then for each item from the combination list, you want to get the number of records that contain this combination item value as a column value.
As a result, you want to return a single integer that is a total count of all records for each combination value.

Let me show you the code:

```python
import itertools
from dataclasses import dataclass
from kink import inject
from typing import List


@dataclass
class GetTotalNumberOfRecords:
    values: List[str]

@inject
class GetNumberOfRecordsQueryHandler(
    QueryHandler[GetTotalNumberOfRecords, int]
):
    def __init__(self, athena_client: AthenaClient) -> None:
        self._athena_client = athena_client

    def __call__(self, query: GetTotalNumberOfRecords) -> int:
        total_number_of_records = 0

        all_combinations = []
        for i, _ in enumerate(query.values, start=1):
            for item in itertools.combinations(query.values, i):
                if len(item) == 1:
                    all_combinations.append(item[0])
                else:
                    all_combinations.append(
                        " | ".join(sorted(item))
                    )

        athena_queries: List[AthenaQuery] = []

        for item in sorted(all_combinations):
            athena_query = AthenaQuery(
                database_name="my_database",
                sql_statement=f"""SELECT DISTINCT
                COUNT(*) OVER () AS number_of_records
                FROM my_table
                WHERE "my_column"='{item}'
                GROUP BY "my_other_column"
                """,
            )
            athena_queries.append(athena_query)

        self._athena_client.execute_many(*athena_queries)

        for athena_query in athena_queries:
            if not athena_query.is_successful:
                continue

            to_add = int(athena_query.result[0]["number_of_records"])
            total_number_of_records += to_add

        return total_number_of_records
```

What do you think? Now let's imagine how hard it would be if we had to base on a pure boto3 Athena client.

In the above scenario, all we have to care about is our business/query logic. No knowledge of how Athena works under the hood.


## Summary

That is it :wink: That was my journey.

I’ve presented you with a custom Python Athena client that streamlines and elevates the querying experience.

Feel free to use it!
I'd love to hear your thoughts on this implementation.
Do you find it beneficial?
What would you add or change to make it even more powerful?
After taking a peek at the code, how do you feel? Can you envision using it in your projects?

I'm eager to engage with you, our fellow tech enthusiasts, to make my AthenaClient even better.

Happy coding!
