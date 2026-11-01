from contract import (
    DeduplicateContactsInput,
    DeduplicateContactsOutput,
)


def _normalize_email(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()

    if not normalized:
        return None

    return normalized


def _normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = "".join(
        character
        for character in value
        if character in "0123456789"
    )

    if not normalized:
        return None

    return normalized


def deduplicate_contacts(
    inputs: DeduplicateContactsInput,
) -> DeduplicateContactsOutput:
    contacts = inputs.contacts
    count = len(contacts)

    parents = list(range(count))
    ranks = [0] * count

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)

        if left_root == right_root:
            return

        if ranks[left_root] < ranks[right_root]:
            left_root, right_root = right_root, left_root

        parents[right_root] = left_root

        if ranks[left_root] == ranks[right_root]:
            ranks[left_root] += 1

    email_owner: dict[str, int] = {}
    phone_owner: dict[str, int] = {}

    for index, contact in enumerate(contacts):
        email = _normalize_email(contact.email)
        phone = _normalize_phone(contact.phone)

        if email is not None:
            if email in email_owner:
                union(index, email_owner[email])
            else:
                email_owner[email] = index

        if phone is not None:
            if phone in phone_owner:
                union(index, phone_owner[phone])
            else:
                phone_owner[phone] = index

    components: dict[int, list[int]] = {}

    for index in range(count):
        root = find(index)
        components.setdefault(root, []).append(index)

    duplicate_groups = sorted(
        (
            sorted(group)
            for group in components.values()
            if len(group) >= 2
        ),
        key=lambda group: group[0],
    )

    duplicate_count = sum(
        len(group)
        for group in duplicate_groups
    )

    return DeduplicateContactsOutput(
        duplicate_groups=duplicate_groups,
        duplicate_count=duplicate_count,
    )