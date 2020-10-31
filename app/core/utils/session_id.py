import uuid

class SessionID:
    @staticmethod
    def get():
        return str(uuid.uuid4())