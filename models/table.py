from dataclasses import dataclass, field
from models.member import Member

@dataclass
class Table:
    id:str
    name:str
    capacity:int=4
    members:dict[str,Member]=field(default_factory=dict)


    def is_full(self)->bool:
        return len(self.members)>=self.capacity

    def add_member(self,member:Member)->None:
        if self.is_full():
            raise ValueError(f"{self.name} is full")
        if member.id in self.members:
            return

        self.members[member.id] = member
        member.assign_table(self.id)

    def remove_member(self,member_id:str)->Member|None:
        member=self.members.pop(member_id, None)

        if member:
            member.remove_from_table()
        return member

    def clear (self)->None:
        for member in self.members.values():
            member.remove_from_table()
        self.members.clear()

    def get_member_count(self)->int:
        return len(self.members)





