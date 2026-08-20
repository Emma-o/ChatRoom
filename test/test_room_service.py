from services.room_service import RoomService


def test_create_room():
    service = RoomService()

    room = service.create_room(
        host_name="Isael",
        table_count=3,
        members_per_table=4
    )

    assert room.code in service.rooms
    assert room.host.username == "Isael"
    assert len(room.tables) == 3
    assert room.members_per_table == 4


def test_get_existing_room():
    service = RoomService()

    created_room = service.create_room(
        host_name="Isael"
    )

    found_room = service.get_room(created_room.code)

    assert found_room is created_room


def test_get_room_is_case_insensitive():
    service = RoomService()

    created_room = service.create_room(
        host_name="Isael"
    )

    found_room = service.get_room(
        created_room.code.lower()
    )

    assert found_room is created_room


def test_room_exists():
    service = RoomService()

    room = service.create_room(
        host_name="Isael"
    )

    assert service.room_exists(room.code) is True
    assert service.room_exists("UNKNOWN") is False


def test_delete_room():
    service = RoomService()

    room = service.create_room(
        host_name="Isael"
    )

    service.delete_room(room.code)

    assert service.get_room(room.code) is None