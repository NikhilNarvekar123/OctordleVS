from fastapi import FastAPI, HTTPException
import httpx
from session import UserSession
from typing import Optional
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime

app = FastAPI()
# decide structure for user store -> uuid is key, then user should have list of sessions (each session is a wordle)
user_store = defaultdict()

# TODO -> maybe move pydantic models into diff file so accessible throughout entire backned

# TODO
class ConnectionRequest(BaseModel):
    # uid could be stored in cookies and sent on initial request to reconnect
    uid: Optional[str] = None
    # addl connection properties here

# TODO
class ConnectionResponse(BaseModel):
    # return uid to user
    uid: str
    # whether user alr exists
    new_session: bool

# TODO - maybe could reuse another request obj (probably leave UID var in higher level object)
class StartTimeRequest(BaseModel):
    # uid
    uid: str

# TODO - maybe could reuse another request obj
class StartTimeResponse(BaseModel):
    # uid
    uid: str
    # whether start time was set or not
    success: bool

# TODO
class GuessRequest(BaseModel):
    # uid
    uid: str
    # answer
    answer: str
    # guess
    guess: str

# TODO
class GuessResponse(BaseModel):
    # uid
    uid: str
    # whether guess was correct
    correct: bool
    # return what letters of guess were correct
    part_correct: Optional[str] = None
    # if guess was successful then return total time taken to guess word
    time_taken: Optional[int] = None
    # error (if err occurred)
    error: Optional[bool] = None



# retrieves random 5 letter word from random-word-api
@app.get('/word')
async def get_random_word():
    url = 'https://random-word-api.vercel.app/api?words=1&length=5'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch random word")


# assign user unique id and create a session
@app.post("/connect/")
async def connect(connection_req: ConnectionRequest):
    if connection_req.uid in user_store:
        return ConnectionResponse(uid=connection_req.uid, new_session=False)
    userSesh = UserSession()
    user_store[userSesh.get_uid()] = {}
    return ConnectionResponse(uid=userSesh.get_uid(), new_session=True)

# set puzzle start time
# if want to keep answer in backend, would make it so that in this method
# the server gets random word and stores it in user session obj to compare to in guess calls
@app.post("/setstarttime")
async def set_start_time(start_time_req: StartTimeRequest):
    if start_time_req.uid in user_store:
        current_time = datetime.now()
        user_store[start_time_req.uid]['starttime'] = current_time
        return StartTimeResponse(uid=start_time_req.uid, success=True)
    else:
        return StartTimeResponse(uid=start_time_req.uid, success=False)
    
# check guess
@app.post("/checkguess")
async def set_start_time(guess_req: GuessRequest):
    if guess_req.uid in user_store:
        current_time = datetime.now()
        if guess_req.answer == guess_req.guess:
            user_store[guess_req.uid]['endtime'] = current_time
            time_taken = int((current_time - user_store[guess_req.uid]['starttime']).total_seconds())
            return GuessResponse(uid=guess_req.uid, correct=True, time_taken=time_taken)
        else:
            common_chars = [char1 if char1 == char2 else ' ' for char1, char2 in zip(guess_req.answer, guess_req.guess)]
            res = ''.join(common_chars)
            return GuessResponse(uid=guess_req.uid, correct=False, part_correct=res)
    else:
        return GuessResponse(uid=guess_req.uid, correct=False, error=True)