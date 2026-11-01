from contract import TASKS, TOOLS, Task, Tool


def _normalize_email(value):
    if value is None:
        return None

    normalized = value.strip().lower()

    if normalized == "":
        return None

    return normalized


def _normalize_phone(value):
    if value is None:
        return None

    normalized = "".join(
        character
        for character in value
        if character in "0123456789"
    )

    if normalized == "":
        return None

    return normalized


def _valid_contacts(inputs):
    if not isinstance(inputs, dict):
        return False

    if "contacts" not in inputs:
        return False

    contacts = inputs["contacts"]

    if not isinstance(contacts, list):
        return False

    for contact in contacts:
        if not isinstance(contact, dict):
            return False

        if "name" not in contact:
            return False

        if not isinstance(contact["name"], str):
            return False

        if "email" not in contact:
            return False

        if contact["email"] is not None and not isinstance(contact["email"], str):
            return False

        if "phone" not in contact:
            return False

        if contact["phone"] is not None and not isinstance(contact["phone"], str):
            return False

    return True


def _expected(inputs):
    contacts = inputs["contacts"]
    count = len(contacts)

    parents = list(range(count))
    ranks = [0] * count

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left, right):
        left_root = find(left)
        right_root = find(right)

        if left_root == right_root:
            return

        if ranks[left_root] < ranks[right_root]:
            left_root, right_root = right_root, left_root

        parents[right_root] = left_root

        if ranks[left_root] == ranks[right_root]:
            ranks[left_root] += 1

    email_owner = {}
    phone_owner = {}

    for index, contact in enumerate(contacts):
        email = _normalize_email(contact["email"])
        phone = _normalize_phone(contact["phone"])

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

    components = {}

    for index in range(count):
        root = find(index)
        components.setdefault(root, []).append(index)

    groups = sorted(
        (
            sorted(group)
            for group in components.values()
            if len(group) >= 2
        ),
        key=lambda group: group[0],
    )

    return {
        "duplicate_groups": groups,
        "duplicate_count": sum(len(group) for group in groups),
    }


def verify_input(tool, inputs):
    if tool != Tool.DEDUPLICATE_CONTACTS:
        return "unknown tool"

    if not _valid_contacts(inputs):
        return "invalid contacts input"

    for index, contact in enumerate(inputs["contacts"]):
        if contact["email"] is not None:
            if not isinstance(contact["email"], str):
                return f"contacts[{index}].email must be a string or null"

        if contact["phone"] is not None:
            if not isinstance(contact["phone"], str):
                return f"contacts[{index}].phone must be a string or null"

    return None


def verify_output(tool, inputs, output, ctx):
    if tool != Tool.DEDUPLICATE_CONTACTS:
        return "unknown tool"

    problem = verify_input(tool, inputs)

    if problem is not None:
        return problem

    if not isinstance(output, dict):
        return "output must be a dictionary"

    expected = _expected(inputs)

    required_fields = (
        "duplicate_groups",
        "duplicate_count",
    )

    for field in required_fields:
        if field not in output:
            return f"missing field: {field}"

    if not isinstance(output["duplicate_groups"], list):
        return "duplicate_groups must be a list"

    if not isinstance(output["duplicate_count"], int):
        return "duplicate_count must be an integer"

    if isinstance(output["duplicate_count"], bool):
        return "duplicate_count must be an integer, not bool"

    for group_index, group in enumerate(output["duplicate_groups"]):
        if not isinstance(group, list):
            return f"duplicate_groups[{group_index}] must be a list"

        for member_index, member in enumerate(group):
            if not isinstance(member, int) or isinstance(member, bool):
                return (
                    f"duplicate_groups[{group_index}]"
                    f"[{member_index}] must be an integer"
                )

    checks = (
        (
            "duplicate_groups",
            expected["duplicate_groups"],
            output["duplicate_groups"],
        ),
        (
            "duplicate_count",
            expected["duplicate_count"],
            output["duplicate_count"],
        ),
    )

    for field, exp, act in checks:
        if exp != act:
            return f"{field}: expected {exp!r}, got {act!r}"

    return None


def verify_task(task, tools, inputs, output, ctx):
    if task != Task.DEDUPLICATE_CONTACTS:
        return "unknown task"

    if isinstance(tools, str):
        supplied_tools = {tools}
    else:
        try:
            supplied_tools = set(tools)
        except TypeError:
            return "tools must be a string or iterable"

    if Tool.DEDUPLICATE_CONTACTS not in supplied_tools:
        return "required tool missing: deduplicate_contacts"

    return verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        output,
        ctx,
    )