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
	# cursor = await app.db_connection.execute(f"SELECT name FROM tracks WHERE composer LIKE '%{composer_name}%' ORDER BY name")
	cursor = await app.db_connection.execute("SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name",
		(composer_name, ))
	tracks = await cursor.fetchall()
	if len(tracks) == 0:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail": {"error": "Not found"}}
	return tracks


class Album(BaseModel):
    title: str
    artist_id: int


async def check_if_row_in_table(name: str, value, table: str) -> bool:
    cursor = await app.db_connection.execute(f"SELECT * FROM {table} WHERE {name} = {value}")
    data = await cursor.fetchall()
    if len(data) == 0:
        return False
    return True


@app.post("/albums/")
async def add_album(response: Response, album: Album):
    if check_if_row_in_table("artist_id", album.artist_id, "artists") == False:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Not found"}}
    cursor = await app.db_connection.execute("INSERT INTO albums(Title, ArtistId) VALUES (?,?)", (album.title, album.artist_id))
    await app.db_connection.commit()
    response.status_code = status.HTTP_201_CREATED
    return {
        "AlbumId": cursor.lastrowid, 
        "Title": album.title, 
        "ArtistId": album.artist_id
        }


@app.get("/albums/{album_id}")
async def get_album(response: Response, album_id: int):
    app.db_connection.row_factory = aiosqlite.Row
    cursor = await app.db_connection.execute("SELECT Title, ArtistId FROM albums WHERE AlbumId = ?", (album_id))
    data = await cursor.fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Not Found"}}
    return data
