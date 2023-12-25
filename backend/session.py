from uuid import uuid4
from error import SessionNotFound    


# represents every individual wordle game
class GameSession:
    
    def __init__(self, id) -> None:
        self.id = id
        self.start_time = None
        # once end-time is set the session is "declared" dead
        self.end_time = None
        self.word = None
        self.num_guesses = 0

    # calculates time taken to finish game in seconds
    def get_time_taken(self) -> int:
        diff = (self.end_time - self.start_time).total_seconds()
        return int(diff)
    
    # checks a guessed word against the session's chosen word
    def check_guess(self, guess) -> (bool, str):
        self.num_guesses += 1
        
        if guess == self.word:
            return (True, "")
        
        # calc common chars and return
        common_chars = [char1 if char1 == char2 else ' ' for char1, char2 in zip(self.word, guess)]
        res = ''.join(common_chars)
        return (False, res)


# represents every individual client in the game
class User:

    def __init__(self) -> None:
        self.uid = str(uuid4())
        self.cur_session_id = 0
        new_sesh = GameSession(0)
        self.history = {new_sesh.id: new_sesh}
    
    # retrieves a session from history based on id
    def get_session(self, sesh_id) -> GameSession:
        if sesh_id in self.history:
            return self.history[sesh_id]
        else:
            return SessionNotFound("No session with matching id")
    
    # makes new session
    def make_new_session(self) -> GameSession:
        self.cur_session_id += 1
        new_sesh = GameSession(self.cur_session_id)
        self.history[new_sesh.id] = new_sesh
        return new_sesh

    # gets current active session
    # TODO -> decide what to for cur_session_id var once session is completed
    # but new session not yet started
    def get_cur_session(self) -> GameSession:
        return self.history[self.cur_session_id]
