from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.command_bus_examples.command_bus import CommandBus
from src.command_bus_examples.fast_api_example.bootstrap import get_command_bus, get_user_repository
from src.command_bus_examples.fast_api_example.commands import RegisterUser
from src.command_bus_examples.fast_api_example.errors import UserAlreadyExist, UserNotFound, ValidationError
from src.command_bus_examples.fast_api_example.repository import UserRepository
from src.entity_id import EntityId

app = FastAPI()


class RegisterUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str


@app.post("/users", status_code=201)
async def register_user(
    request: RegisterUserRequest, command_bus: Annotated[CommandBus, Depends(get_command_bus)]
) -> JSONResponse:
    user_id = EntityId.new_one()
    command_bus.execute(RegisterUser(user_id, request.first_name, request.last_name, request.email))

    return JSONResponse(content={}, headers={"Location": f"/users/{user_id}"})


@app.get("/users/{user_id}")
async def get_user(
    user_id: str, user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> JSONResponse:
    user = user_repository.get(EntityId.of(user_id))
    return JSONResponse(content={"id": str(user.id), "full_name": user.full_name, "email": user.email})


@app.exception_handler(UserNotFound)
async def user_not_found_exception_handler(request: Request, exc: UserNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"message": f"Oops! {exc}"},
    )


@app.exception_handler(UserAlreadyExist)
async def user_already_exist_exception_handler(request: Request, exc: UserAlreadyExist) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"message": f"Oops! {exc}"},
    )


@app.exception_handler(ValidationError)
async def validation_error_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"message": f"Oops! {exc}"},
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
