class DomainError(Exception):
    pass


class ResourceNotFound(DomainError):
    def __init__(self, resource_id: str) -> None:
        super().__init__(f"Resource with id={resource_id} was not found!")


class BorrowingError(DomainError):
    pass
