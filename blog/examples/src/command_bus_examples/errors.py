from __future__ import annotations

from src.command_bus_examples.command import Command


class CommandAlreadyRegistered(Exception):
    @classmethod
    def for_command(cls, command_type: str) -> CommandAlreadyRegistered:
        return cls(f"`{command_type}` has been already registered!")


class HandlerNotFound(Exception):
    @classmethod
    def for_command(cls, command: Command) -> HandlerNotFound:
        return cls(f"No handler has been found for {command}!")
