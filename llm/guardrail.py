from enum import StrEnum
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    ...


class ContentDirectionType(StrEnum):
    INPUT = "input"
    OUTPUT  = "output"


class GuardrailService:
    def __init__(self):
        ...


    async def check_input(self, content: str) -> GuardrailResult:
        return await self._check_contents(content, ContentDirectionType.INPUT)

    async def check_output(self, content: str) -> GuardrailResult:
        return await self._check_contents(content, ContentDirectionType.OUTPUT)

    async def _check_contents(self, content: str, direction: ContentDirectionType) -> GuardrailResult:
        ...