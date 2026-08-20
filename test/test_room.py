import pytest

from models.member import Member
from models.room import Room


def create_test_room() -> Room:
    host = Member(
        id="host-1",
        username="Isael",
        role="host",
        approved=True
    )

    return Room(
        code="ROOM1234",
        host=host,
        table_count=2,
        members_per_table=2
    )


def test_room_creates_tables():
    room = create_test_room()

    assert len(room.tables) == 2
    assert "table-1" in room.tables
    assert "table-2" in room.tables
    assert room.tables["table-1"].capacity == 2


def test_host_is_added_to_room():
    room = create_test_room()

    assert room.host.id in room.members
    assert room.host.role == "host"
    assert room.host.approved is True


def test_add_member_to_waiting_room():
    room = create_test_room()

    participant = Member(
        id="member-1",
        username="Carlos"
    )

    room.add_to_waiting_room(participant)

    assert participant.id in room.waiting_members
    assert participant.id not in room.members


def test_approve_member():
    room = create_test_room()

    participant = Member(
        id="member-1",
        username="Carlos"
    )

    room.add_to_waiting_room(participant)
    approved_member = room.approve_member(participant.id)

    assert approved_member.approved is True
    assert participant.id in room.members
    assert participant.id not in room.waiting_members


def test_approve_unknown_member_raises_error():
    room = create_test_room()

    with pytest.raises(
        ValueError,
        match="Member is not in the waiting room"
    ):
        room.approve_member("unknown-member")


def test_assign_members_to_tables():
    room = create_test_room()

    participants = [
        Member(
            id=f"member-{index}",
            username=f"User {index}",
            approved=True
        )
        for index in range(1, 5)
    ]

    for participant in participants:
        room.members[participant.id] = participant

    room.assign_members_to_tables()

    assigned_member_count = sum(
        table.get_member_count()
        for table in room.tables.values()
    )

    assert assigned_member_count == 4
    assert room.status == "active"

    for participant in participants:
        assert participant.table_id is not None


def test_not_enough_table_capacity():
    room = create_test_room()

    for index in range(1, 6):
        participant = Member(
            id=f"member-{index}",
            username=f"User {index}",
            approved=True
        )

        room.members[participant.id] = participant

    with pytest.raises(
        ValueError,
        match="There are not enough spaces at the tables"
    ):
        room.assign_members_to_tables()


def test_move_member_to_another_table():
    room = create_test_room()

    participant = Member(
        id="member-1",
        username="Carlos",
        approved=True
    )

    room.members[participant.id] = participant
    room.tables["table-1"].add_member(participant)

    room.move_member(
        member_id=participant.id,
        new_table_id="table-2"
    )

    assert participant.id not in room.tables["table-1"].members
    assert participant.id in room.tables["table-2"].members
    assert participant.table_id == "table-2"


def test_host_cannot_be_removed():
    room = create_test_room()

    with pytest.raises(
        ValueError,
        match="The host cannot be removed"
    ):
        room.remove_member(room.host.id)