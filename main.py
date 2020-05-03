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


@app.post("/albums/")
async def add_album(response: Response, album: Album):
    cursor = await app.db_connection.execute(f"SELECT ArtistId FROM artists WHERE ArtistId = ?", (album.artist_id, ))
    result = await cursor.fetchone()
    if result is None:
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
    cursor = await app.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?", (album_id, ))
    data = await cursor.fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Not Found"}}
    return data


class Customer(BaseModel):
    company: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None
    postalcode: str = None
    fax: str = None


@app.put("/customers/{customer_id}")
async def customer_edit(response: Response, customer: Customer, customer_id: int):
    cursor = await app.db_connection.execute("SELECT * from customers WHERE CustomerId = ?", (customer_id,))
    data = await cursor.fetchone()
    print(data)
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail":{"error":"Not Found"}}
    update_customer = customer.dict(exclude_unset=True)

    if len(update_customer) != 0:
        setters: str = ""
        for key in update_customer.keys():
            setters += f"{key}=?,"
        setters = setters[:-1]
        query = f"UPDATE customers SET {setters} WHERE CustomerId = ?"

        values = list(update_customer.values())
        values.append(customer_id)

        cursor = await app.db_connection.execute(query, values)
        await app.db_connection.commit()
    app.db_connection.row_factory = aiosqlite.Row
    cursor = await app.db_connection.execute("SELECT * FROM customers WHERE CustomerId = ?",
        (customer_id, ))
    customer = await cursor.fetchone()
    return customer
 
@app.get("/sales")
async def get_sales_stats(category: str):
    app.db_connection.row_factory = aiosqlite.Row
    if category == "customers":
        cursor = await app.db_connection.execute(
            '''SELECT customers.CustomerId, Email, Phone, ROUND(SUM(Total), 2) AS Sum
            FROM invoices JOIN customers on invoices.CustomerId = customers.CustomerId
            GROUP BY invoices.CustomerId ORDER BY Sum DESC, invoices.CustomerId''')
        data = await cursor.fetchall()
        return data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Unsuported category."}}