from dataclasses import dataclass
from typing import Optional

@dataclass
class Member:
    id: str
    username: str
    role: str="Participant"
    approved: bool=False
    table_id:Optional[str]=None
    socket_id : Optional[str]=None
    camera_enabled:bool=False
    microphone_enabled:bool=False

    def approve(self)->None:
        self.approved = True

    def reject(self)->None:
        self.approved = False
        self.table_id = None

    def assign_table(self, table_id:str) -> None:
        self.table_id = table_id
        self.camera_enabled = False
        self.microphone_enabled = False

    def remove_from_table(self)->None:
        self.table_id = None
        self.camera_enabled = False
        self.microphone_enabled = False
