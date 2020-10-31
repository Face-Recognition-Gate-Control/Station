from core.utils.session_id import SessionID
from core.utils.command import Command


camera_command = Command()
session_id = SessionID.get()

print("camera_command: ", camera_command())
print("session_id: ", session_id)
