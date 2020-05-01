import secrets
from typing import Dict, Optional

from fastapi import Depends, FastAPI, Response, status, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie, HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette.responses import RedirectResponse


import aiosqlite


class DaftAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.security = HTTPBasic(auto_error=False)
        self.secret_key = "kluczyk"
        self.API_KEY = "session"
        self.cookie_sec = APIKeyCookie(name=self.API_KEY, auto_error=False)
        self.templates = Jinja2Templates(directory="templates")


app = DaftAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = await aiosqlite.connect('db/chinook.db')


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()




# # # HOW TO USE ASYNC SQLITE
# @app.get("/data")
#  async def root():
#     cursor = await app.db_connection.execute("....")
#     data = await cursor.fetchall()
#     return {"data": data}


@app.get("/")
async def get_tracks(page: int = 0, per_page: int = 10):
    cursor = await app.db_connection.execute(f"SELECT * FROM tracks  ORDER BY TrackId LIMIT {per_page} OFFSET {per_page * page}")
    data = await cursor.fetchall()
    return data
