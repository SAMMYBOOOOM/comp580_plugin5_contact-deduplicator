from contract import (
    ContactInput,
    DeduplicateContactsInput,
)
from plugin.deduplicate_contacts import deduplicate_contacts


def contact(name, email=None, phone=None):
    return ContactInput(
        name=name,
        email=email,
        phone=phone,
    )


def run(*contacts):
    return deduplicate_contacts(
        DeduplicateContactsInput(contacts=list(contacts))
    )


def test_email_duplicate():
    result = run(
        contact("Alice", "alice@example.com"),
        contact("Alice Smith", "ALICE@EXAMPLE.COM"),
    )

    assert result.duplicate_groups == [[0, 1]]
    assert result.duplicate_count == 2


def test_email_whitespace():
    result = run(
        contact("Alice", " alice@example.com "),
        contact("Alice", "alice@example.com"),
    )

    assert result.duplicate_groups == [[0, 1]]


def test_phone_duplicate():
    result = run(
        contact("Alice", phone="(123) 456-7890"),
        contact("Bob", phone="1234567890"),
    )

    assert result.duplicate_groups == [[0, 1]]


def test_email_or_phone_matching():
    result = run(
        contact("Alice", "shared@example.com"),
        contact("Bob", "shared@example.com", "5551234567"),
        contact("Charlie", "charlie@example.com", "555-123-4567"),
    )

    assert result.duplicate_groups == [[0, 1, 2]]
    assert result.duplicate_count == 3


def test_transitive_matching():
    result = run(
        contact("A", "a@example.com", None),
        contact("B", "a@example.com", "12345"),
        contact("C", "c@example.com", "12345"),
    )

    assert result.duplicate_groups == [[0, 1, 2]]


def test_names_are_not_matching_criteria():
    result = run(
        contact("Alice Smith", "alice@example.com"),
        contact("Alice Smith", "different@example.com"),
    )

    assert result.duplicate_groups == []
    assert result.duplicate_count == 0


def test_empty_values_do_not_match():
    result = run(
        contact("A", "", ""),
        contact("B", " ", " "),
        contact("C", None, None),
    )

    assert result.duplicate_groups == []
    assert result.duplicate_count == 0


def test_unique_contacts():
    result = run(
        contact("A", "a@example.com", "111"),
        contact("B", "b@example.com", "222"),
        contact("C", "c@example.com", "333"),
    )

    assert result.duplicate_groups == []
    assert result.duplicate_count == 0


def test_multiple_independent_groups():
    result = run(
        contact("A", "a@example.com"),
        contact("B", "a@example.com"),
        contact("C", "c@example.com"),
        contact("D", "c@example.com"),
        contact("E", "e@example.com"),
    )

    assert result.duplicate_groups == [[0, 1], [2, 3]]
    assert result.duplicate_count == 4


def test_original_indices_are_preserved():
    result = run(
        contact("A", "a@example.com"),
        contact("B", "unique@example.com"),
        contact("C", "a@example.com"),
        contact("D", "another@example.com"),
    )

    assert result.duplicate_groups == [[0, 2]]
    assert result.duplicate_count == 2