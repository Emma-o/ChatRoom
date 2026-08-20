import random
import uuid
from string import ascii_uppercase
from models.member import Member
from models.room import Room
from models.table import Table

class RoomService:
    def __init__(self):
        self.rooms: dict[str, Room] = {}
        self.messages: dict[str, list[dict]] = {}

    def generate_unique_code(self, length=4):
        while True:
            code = "".join(
                random.choice(ascii_uppercase)
                for _ in range(length)
            )

            if code not in self.rooms:
                return code




    def create_room(self, host_name: str, table_count:int=4, members_per_table:int = 4)->Room:
        code = self.generate_unique_code()

        host=Member(
            id=str(uuid.uuid4()),
            username=host_name,
            role="host",
            approved=True
        )
        room = Room(
            code=code,
            host=host,
            table_count=table_count,
            members_per_table=members_per_table
        )


        self.rooms[code] = room
        self.messages[code] = []
        return room


    def room_exists(self, code):
        return code in self.rooms

    def get_room(self, code):
        return self.rooms.get(code)

    def get_members(self, code):
        room = self.get_room(code)

        if room is None:
            return []

        return [
            member.username
            for member in room.members.values()
        ]

    def add_member(
            self,
            code: str,
            username: str
    ) -> Member | None:
        room = self.get_room(code)

        if room is None:
            return None

        # Buscar entre los miembros aprobados.
        for member in room.members.values():
            if member.username == username:
                return member

        # Buscar entre los miembros que ya están esperando.
        for member in room.waiting_members.values():
            if member.username == username:
                return member

        member = Member(
            id=str(uuid.uuid4()),
            username=username,
            role="Participant",
            approved=False
        )

        room.add_to_waiting_room(member)

        return member

    def remove_member(
            self,
            code: str,
            member_id: str
    ) -> bool:
        room = self.get_room(code)

        if room is None:
            return False

        member = room.members.get(member_id)

        if member is None:
            return False

        if member.id == room.host.id:
            return False

        room.remove_member(member_id)

        return True

    def add_message(self, code, name, message):
        if not self.room_exists(code):
            return False

        self.messages[code].append({
            "name": name,
            "message": message
        })

        return True

    def get_messages(self, code):
        return self.messages.get(code, [])



    def get_waiting_members(
        self,
        code: str
    ) -> list[dict]:
        room = self.get_room(code)

        if room is None:
            return []

        return [
            {
                "id": member.id,
                "username": member.username
            }
            for member in room.waiting_members.values()
        ]

    def approve_member(
            self,
            code: str,
            member_id: str
    ) -> Member | None:
        room = self.get_room(code)

        if room is None:
            return None

        try:
            return room.approve_member(member_id)
        except ValueError:
            return None

    def reject_member(
            self,
            code: str,
            member_id: str
    ) -> Member | None:
        room = self.get_room(code)

        if room is None:
            return None

        return room.reject_member(member_id)