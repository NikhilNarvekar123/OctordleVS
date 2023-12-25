from fastapi import FastAPI, HTTPException
import httpx
from session import User, GameSession
from typing import Optional
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime


'''
TODO -> testing, edge cases, check if word is valid, improved error-handling
'''


app = FastAPI()


MAX_NUM_GUESSES = 6


# k: UID, v: User Obj
user_store = defaultdict()
# k: UID, v: {'total_games': X, 'wins': Y}
user_stats_store = defaultdict()


# base form of server req
class BaseRequest(BaseModel):
    uid: str

# base form of a server rep
class BaseResponse(BaseModel):
    uid: str
    # whether request was performed successfully
    op_success: bool
    error: Optional[str] = None

# used for initial client-server connection
class ConnectionRequest(BaseModel):
    uid: Optional[str] = None

# used for word-guessing reqs
class GuessRequest(BaseRequest):
    guess: str

# responds to a given word-guess
class GuessResponse(BaseResponse):
    # return what letters of guess were correct
    part_correct: Optional[str] = None
    time_taken: Optional[int] = None
    is_last_guess: Optional[bool] = None


# invoked when client loads in
# TODO -> should successful connect to existing UID give success var as false?
@app.post("/connect")
async def connect(connection_req: ConnectionRequest):
    if connection_req.uid in user_store:
        return BaseResponse(uid=connection_req.uid, op_success=False)
    user = User()
    user_store[user.uid] = user
    user_stats_store[user.uid] = {'total_games': 0, 'wins': 0}
    return BaseResponse(uid=user.uid, op_success=True)

# starts a game session for the given client
@app.post("/start_game")
async def start_game(start_game_req: BaseRequest):
    if not start_game_req.uid in user_store:
        return BaseResponse(uid=start_game_req.uid, op_success=False, error="Invalid UID")
    
    user = user_store[start_game_req.uid]
    cur_sesh = user.make_new_session()

    if user.uid in user_stats_store:
        user_stats_store[user.uid]['total_games'] += 1
    
    # retrieve random word
    url = 'https://random-word-api.vercel.app/api?words=1&length=5'
    word = None
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            word = response.content.decode('utf-8')[2:-2]
            print(word)
        else:
            error_msg = response.status_code + ": Failed to fetch random word"
            return BaseResponse(uid=start_game_req.uid, op_success=False, error=error_msg)
    
    # update sesh
    cur_sesh.word = word
    cur_sesh.start_time = datetime.now()
    return BaseResponse(uid=user.uid, op_success=True)

# check guess on every user word submit
@app.post("/check_guess")
async def check_guess(guess_req: GuessRequest):
    if not guess_req.uid in user_store:
        return GuessResponse(uid=guess_req.uid, op_success=False, error="Invalid UID")

    current_time = datetime.now()
    cur_sesh = user_store[guess_req.uid].get_cur_session()

    # prevent more than max guesses (redundant but in-case endpoint is called after session end)
    if not cur_sesh.num_guesses < MAX_NUM_GUESSES:
        return GuessResponse(uid=guess_req.uid, op_success=False, error="Guesses Exceeded")

    res = cur_sesh.check_guess(guess_req.guess)

    if res[0] == False:
        # wrong guess
        return GuessResponse(
            uid=guess_req.uid,
            op_success=False,
            part_correct=res[1],
            is_last_guess=(cur_sesh.num_guesses >= MAX_NUM_GUESSES)
        )
    else:
        # right guess
        cur_sesh.end_time = current_time
        user_stats_store[guess_req.uid]['wins'] += 1

        return GuessResponse(
            uid=guess_req.uid,
            op_success=True,
            part_correct=res[1],
            time_taken=cur_sesh.get_time_taken(),
            is_last_guess=(cur_sesh.num_guesses >= MAX_NUM_GUESSES)
        )
