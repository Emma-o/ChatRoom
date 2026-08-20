import pytest

from models.member import Member
from models.table import Table


def test_add_member_to_table():
    table = Table(
        id="table-1",
        name="Table 1",
        capacity=4
    )

    member = Member(
        id="member-1",
        username="Isael",
        approved=True
    )

    table.add_member(member)

    assert member.id in table.members
    assert member.table_id == table.id
    assert table.get_member_count() == 1


def test_table_is_full():
    table = Table(
        id="table-1",
        name="Table 1",
        capacity=2
    )

    member_1 = Member(id="1", username="Isael")
    member_2 = Member(id="2", username="Carlos")

    table.add_member(member_1)
    table.add_member(member_2)

    assert table.is_full() is True


def test_cannot_add_member_to_full_table():
    table = Table(
        id="table-1",
        name="Table 1",
        capacity=1
    )

    table.add_member(
        Member(id="1", username="Isael")
    )

    with pytest.raises(ValueError, match="Table 1 is full"):
        table.add_member(
            Member(id="2", username="Carlos")
        )


def test_remove_member_from_table():
    table = Table(
        id="table-1",
        name="Table 1",
        capacity=4
    )

    member = Member(id="1", username="Isael")

    table.add_member(member)
    removed_member = table.remove_member(member.id)

    assert removed_member == member
    assert member.id not in table.members
    assert member.table_id is None