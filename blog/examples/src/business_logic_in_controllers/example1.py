import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Annotated, List

import uvicorn
from email_validator import EmailNotValidError, validate_email
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from src.entity_id import EntityId

app = FastAPI()


class CreateArticleRequest(BaseModel):
    title: str
    content: str
    tags: List[str]
    categories: List[str]
    reviewers: List[EmailStr]


class Status(Enum):
    PUBLISHED = "PUBLISHED"
    DRAFT = "DRAFT"


@dataclass
class Article:
    id: EntityId
    title: str
    content: str
    created_at: datetime
    status: Status


class ArticleRepository(ABC):
    @abstractmethod
    def save(self, article: Article) -> None:
        pass


def get_article_repository() -> ArticleRepository:  # type: ignore
    pass


@app.post("/articles", status_code=201)
async def create_article(
    request: CreateArticleRequest, repository: Annotated[ArticleRepository, Depends(get_article_repository)]
) -> JSONResponse:
    if len(request.tags) > 10:
        raise HTTPException(status_code=400, detail="Number of tags may not be bigger than 10!")

    if len(request.title.split(" ")) < 5:
        raise HTTPException(status_code=400, detail="Title may not be smaller than 5 words!")

    if len(re.findall(r"\w+", request.content)) < 50:
        raise HTTPException(status_code=400, detail="Content of the article may not be smaller than 50 words!")

    if len(request.categories) < 1:
        raise HTTPException(status_code=400, detail="Article has to have at least one category!")

    reviewers: List[str] = []
    for email in reviewers:
        try:
            validated_email = validate_email(email, check_deliverability=False)
            reviewers.append(validated_email)
        except EmailNotValidError:
            raise HTTPException(status_code=400, detail=f"Provided reviewer email address `{email}` is not correct")

    if len(reviewers) < 2:
        raise HTTPException(status_code=400, detail="Article has to have at least 2 reviewers")

    article_id = EntityId.new_one()
    article = Article(
        id=article_id, title=request.title, content=request.content, created_at=datetime.utcnow(), status=Status.DRAFT
    )

    repository.save(article)

    for reviewer in request.reviewers:
        notify_reviewers(reviewer)

    return JSONResponse(content={}, headers={"Location": f"/articles/{article.id}"})


def notify_reviewers(reviewer: str) -> None:
    print(f"Notifying reviewer {reviewer} that a new article is awaiting his review!")


if __name__ == "__main__":
    uvicorn.run("example1:app", host="127.0.0.1", port=8000, reload=True)
