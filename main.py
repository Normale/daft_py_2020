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


@app.get("/tracks")
async def get_tracks(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = aiosqlite.Row
    cursor = await app.db_connection.execute(f"SELECT * FROM tracks  ORDER BY TrackId LIMIT {per_page} OFFSET {per_page * page}")
    data = await cursor.fetchall()
    return data



@app.get("/tracks/composers/")
async def tracks_composers(response: Response, composer_name: str):
	app.db_connection.row_factory = lambda cursor, x: x[0]
	cursor = await app.db_connection.execute(f"SELECT name FROM tracks WHERE composer LIKE '%{composer_name}%' ORDER BY name")
	tracks = await cursor.fetchall()
	if len(tracks) == 0:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Not found"}}
	return tracks



