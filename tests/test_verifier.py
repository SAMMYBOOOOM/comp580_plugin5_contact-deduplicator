from contract import Task, Tool
from verifier import verify_input, verify_output, verify_task


def make_contact(name, email=None, phone=None):
    return {
        "name": name,
        "email": email,
        "phone": phone,
    }


def make_input(*contacts):
    return {"contacts": list(contacts)}


def expected_output(inputs, **overrides):
    contacts = inputs["contacts"]
    parents = list(range(len(contacts)))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left, right):
        left_root = find(left)
        right_root = find(right)

        if left_root != right_root:
            parents[right_root] = left_root

    emails = {}
    phones = {}

    for index, contact in enumerate(contacts):
        email = contact["email"]
        phone = contact["phone"]

        normalized_email = (
            email.strip().lower()
            if email is not None
            else ""
        )

        normalized_phone = (
            "".join(c for c in phone if c in "0123456789")
            if phone is not None
            else ""
        )

        if normalized_email:
            if normalized_email in emails:
                union(index, emails[normalized_email])
            else:
                emails[normalized_email] = index

        if normalized_phone:
            if normalized_phone in phones:
                union(index, phones[normalized_phone])
            else:
                phones[normalized_phone] = index

    components = {}

    for index in range(len(contacts)):
        components.setdefault(find(index), []).append(index)

    groups = sorted(
        (
            group
            for group in components.values()
            if len(group) >= 2
        ),
        key=lambda group: group[0],
    )

    result = {
        "duplicate_groups": groups,
        "duplicate_count": sum(len(group) for group in groups),
    }

    result.update(overrides)
    return result


def test_valid_input():
    inputs = make_input(
        make_contact("Alice", "alice@example.com"),
        make_contact("Bob", "bob@example.com"),
    )

    assert verify_input(Tool.DEDUPLICATE_CONTACTS, inputs) is None


def test_invalid_tool():
    assert verify_input("unknown", {"contacts": []}) == "unknown tool"


def test_missing_contacts():
    assert verify_input(
        Tool.DEDUPLICATE_CONTACTS,
        {},
    ) == "invalid contacts input"


def test_contacts_wrong_type():
    assert verify_input(
        Tool.DEDUPLICATE_CONTACTS,
        {"contacts": "not a list"},
    ) == "invalid contacts input"


def test_contact_wrong_type():
    assert verify_input(
        Tool.DEDUPLICATE_CONTACTS,
        {"contacts": ["not a contact"]},
    ) == "invalid contacts input"


def test_missing_name():
    inputs = {
        "contacts": [
            {"email": "a@example.com", "phone": None}
        ]
    }

    assert verify_input(Tool.DEDUPLICATE_CONTACTS, inputs) is not None


def test_wrong_email_type():
    inputs = make_input(make_contact("Alice", 123))

    assert verify_input(Tool.DEDUPLICATE_CONTACTS, inputs) is not None


def test_wrong_phone_type():
    inputs = make_input(make_contact("Alice", None, 123))

    assert verify_input(Tool.DEDUPLICATE_CONTACTS, inputs) is not None


def test_correct_output():
    inputs = make_input(
        make_contact("Alice", "alice@example.com"),
        make_contact("Bob", "ALICE@example.com"),
        make_contact("Charlie", "charlie@example.com"),
    )

    output = expected_output(inputs)

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        output,
        None,
    ) is None


def test_wrong_duplicate_groups():
    inputs = make_input(
        make_contact("Alice", "alice@example.com"),
        make_contact("Bob", "alice@example.com"),
    )

    output = expected_output(
        inputs,
        duplicate_groups=[[0]],
    )

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        output,
        None,
    ).startswith("duplicate_groups:")


def test_wrong_duplicate_count():
    inputs = make_input(
        make_contact("Alice", "alice@example.com"),
        make_contact("Bob", "alice@example.com"),
    )

    output = expected_output(
        inputs,
        duplicate_count=1,
    )

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        output,
        None,
    ).startswith("duplicate_count:")


def test_missing_output_field():
    inputs = make_input(make_contact("Alice"))
    output = {"duplicate_groups": []}

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        output,
        None,
    ) == "missing field: duplicate_count"


def test_boolean_is_not_integer():
    inputs = make_input(make_contact("Alice"))
    output = expected_output(inputs, duplicate_count=True)

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        output,
        None,
    ) == "duplicate_count must be an integer, not bool"


def test_output_not_dictionary():
    inputs = make_input(make_contact("Alice"))

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        [],
        None,
    ) == "output must be a dictionary"


def test_unknown_task():
    assert verify_task(
        "unknown",
        ["deduplicate_contacts"],
        {"contacts": []},
        {},
        None,
    ) == "unknown task"


def test_missing_required_tool():
    assert verify_task(
        Task.DEDUPLICATE_CONTACTS,
        [],
        {"contacts": []},
        {},
        None,
    ) == "required tool missing: deduplicate_contacts"


def test_task_verification():
    inputs = make_input(
        make_contact("Alice", "alice@example.com"),
        make_contact("Bob", "alice@example.com"),
    )

    output = expected_output(inputs)

    assert verify_task(
        Task.DEDUPLICATE_CONTACTS,
        "deduplicate_contacts",
        inputs,
        output,
        None,
    ) is None


def test_null_optional_values():
    inputs = make_input(
        make_contact("Alice", None, None),
    )

    assert verify_input(Tool.DEDUPLICATE_CONTACTS, inputs) is None

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        expected_output(inputs),
        None,
    ) is None


def test_empty_and_whitespace_values():
    inputs = make_input(
        make_contact("A", "", ""),
        make_contact("B", " ", " "),
    )

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        expected_output(inputs),
        None,
    ) is None


def test_phone_boundary_digits():
    inputs = make_input(
        make_contact("A", None, "1"),
        make_contact("B", None, "1"),
    )

    assert verify_output(
        Tool.DEDUPLICATE_CONTACTS,
        inputs,
        expected_output(inputs),
        None,
    ) is None