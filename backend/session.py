from uuid import uuid4

class UserSession:
    
    # generate random uuid
    def __init__(self) -> None:
        self.uid = str(uuid4())

    # get uid
    def get_uid(self) -> str:
        return self.uid
