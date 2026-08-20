import math
import random
from dataclasses import dataclass, field

from models.member import Member
from models.table import Table


@dataclass
class Room:
    code: str
    host: Member
    table_count: int = 2
    members_per_table: int = 4
    status: str = "waiting"

    members: dict[str, Member] = field(default_factory=dict)
    waiting_members: dict[str, Member] = field(default_factory=dict)
    tables: dict[str, Table] = field(default_factory=dict)

    def start_tables(
            self,
            members_per_table: int
    ) -> None:
        if self.status == "active" or self.tables:
            raise ValueError(
                "Tables have already been created"
            )

        if members_per_table < 2:
            raise ValueError(
                "Each table must have at least 2 members"
            )

        participants = [
            member
            for member in self.members.values()
            if member.id != self.host.id
               and member.approved
        ]

        if len(participants) < 2:
            raise ValueError(
                "At least 2 approved participants are required"
            )

        self.members_per_table = members_per_table

        self.create_tables()
        self.assign_members_to_tables()

    def __post_init__(self) -> None:
        self.host.role = "host"
        self.host.approved = True

        self.members[self.host.id] = self.host

    def create_tables(self) -> None:
        if self.status == "active" or self.tables:
            raise ValueError(
                "Tables have already been created"
            )
        participants = [
            member
            for member in self.members.values()
            if member.role.lower() == "participant"
               and member.approved
        ]

        participant_count = len(participants)

        if participant_count == 0:
            self.tables.clear()
            self.table_count = 0
            return

        self.table_count = (
                                   participant_count
                                   + self.members_per_table
                                   - 1
                           ) // self.members_per_table

        self.tables = {
            f"table-{number}": Table(
                id=f"table-{number}",
                name=f"Table {number}",
                capacity=self.members_per_table
            )
            for number in range(
                1,
                self.table_count + 1
            )
        }

    def start_tables(
            self,
            members_per_table: int
    ) -> None:
        if self.status == "active" or self.tables:
            raise ValueError(
                "Tables have already been created"
            )

        if members_per_table < 2:
            raise ValueError(
                "Each table must have at least 2 members"
            )

        participants = [
            member
            for member in self.members.values()
            if member.id != self.host.id
               and member.approved
        ]

        if len(participants) < 2:
            raise ValueError(
                "At least 2 approved participants are required"
            )

        self.members_per_table = members_per_table

        self.create_tables()
        self.assign_members_to_tables()

    def add_to_waiting_room(self, member: Member) -> None:
        if member.id in self.members:
            raise ValueError("Member is already in the room")

        self.waiting_members[member.id] = member

    def approve_member(self, member_id: str) -> Member:
        member = self.waiting_members.pop(
            member_id,
            None
        )

        if member is None:
            raise ValueError(
                "Member is not in the waiting room"
            )

        member.approve()

        self.members[member.id] = member

        return member

    def reject_member(
            self,
            member_id: str
    ) -> Member | None:
        member = self.waiting_members.pop(
            member_id,
            None
        )

        if member:
            member.reject()

        return member

    def remove_member(self, member_id: str) -> Member | None:
        if member_id == self.host.id:
            raise ValueError("The host cannot be removed as a participant")

        member = self.members.pop(member_id, None)

        if member and member.table_id:
            table = self.tables.get(member.table_id)

            if table:
                table.remove_member(member_id)

        self.waiting_members.pop(member_id, None)

        return member

    def assign_members_to_tables(self) -> None:
        participants = [
            member
            for member in self.members.values()
            if member.role.lower() == "participant"
               and member.approved
        ]

        if not self.tables:
            raise ValueError(
                "Tables have not been created"
            )

        available_capacity = sum(
            table.capacity
            for table in self.tables.values()
        )

        if len(participants) > available_capacity:
            raise ValueError(
                "There are not enough spaces at the tables"
            )

        for table in self.tables.values():
            table.clear()

        random.shuffle(participants)

        table_list = list(self.tables.values())

        for index, member in enumerate(participants):
            table = table_list[
                index % len(table_list)
                ]

            table.add_member(member)

        self.status = "active"

    def move_member(self, member_id: str, new_table_id: str) -> None:
        member = self.members.get(member_id)
        new_table = self.tables.get(new_table_id)
        if member.table_id == new_table_id:
            return

        if member is None:
            raise ValueError("Member does not exist")

        if new_table is None:
            raise ValueError("Table does not exist")

        if new_table.is_full():
            raise ValueError("The destination table is full")

        if member.table_id:
            current_table = self.tables.get(member.table_id)

            if current_table:
                current_table.remove_member(member.id)

        new_table.add_member(member)

    def get_state(self) -> dict:
        return {
            "code": self.code,
            "status": self.status,
            "host": self.host.username,
            "waiting_members": [
                {
                    "id": member.id,
                    "username": member.username
                }
                for member in self.waiting_members.values()
            ],
            "tables": {
                table_id: {
                    "id": table.id,
                    "name": table.name,
                    "capacity": table.capacity,
                    "members": [
                        {
                            "id": member.id,
                            "username": member.username
                        }
                        for member in table.members.values()
                    ]
                }
                for table_id, table in self.tables.items()
            }
        }