from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

from slimconfig import Output


class Tool(StrEnum):
    DEDUPLICATE_CONTACTS = "deduplicate_contacts"


class Task(StrEnum):
    DEDUPLICATE_CONTACTS = "deduplicate-contacts"


@dataclass
class ContactInput(Output):
    name: Annotated[str, "Original contact name. Required but never used for matching."]
    email: Annotated[str | None, "Optional email. Matching trims surrounding whitespace and ignores case. Empty values never match."]
    phone: Annotated[str | None, "Optional phone. Matching removes all non-ASCII-digit characters. Empty values never match."]


@dataclass
class DeduplicateContactsInput(Output):
    contacts: Annotated[list[ContactInput], "Contacts in original input order. Indices in the result are zero-based."]


@dataclass
class DeduplicateContactsOutput(Output):
    duplicate_groups: Annotated[list[list[int]], "Duplicate groups containing original zero-based contact indices. Groups and indices are sorted ascending. Only groups containing at least two contacts are returned."]
    duplicate_count: Annotated[int, "Total number of contacts participating in duplicate groups, counting every group member."]


TOOLS = {
    Tool.DEDUPLICATE_CONTACTS: (DeduplicateContactsInput, DeduplicateContactsOutput),
}

TASKS = {
    Task.DEDUPLICATE_CONTACTS: (DeduplicateContactsInput, DeduplicateContactsOutput),
}