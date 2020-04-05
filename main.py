from typing import Dict

from fastapi import FastAPI

from pydantic import BaseModel


app = FastAPI()


@app.get("/")
def get_response():
    return {"method": "GET"}

@app.post("/")
def post_response():
    return  {"method": "POST"}

@app.delete("/")
def delete_response():
    return  {"method": "DELETE"}
    
@app.put("/")
def put_response():
    return  {"method": "PUT"}
