from typing import Dict

from fastapi import FastAPI

from pydantic import BaseModel


app = FastAPI()


@app.get("/method")
def get_response():
    return {"method": "GET"}

@app.post("/method")
def post_response():
    return  {"method": "POST"}

    
@app.put("/method")
def put_response():
    return  {"method": "PUT"}
