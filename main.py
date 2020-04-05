from typing import Dict

from fastapi import FastAPI

from pydantic import BaseModel


app = FastAPI()
app.count = 0

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get("/method")
async def get_response():
    return {"method": "GET"}

@app.post("/method")
async def post_response():
    return  {"method": "POST"}

    
@app.put("/method")
async def put_response():
    return  {"method": "PUT"}
    
@app.delete("/method")
async def del_response():
    return  {"method": "DELETE"}
class Patient_data(BaseModel):
    name: str
    surename: str

class PatientResponse(BaseModel):
    id: int
    patient: Patient_data


@app.post("/patient", response_model=PatientResponse)
def new_patient(rq: Patient_data):
    patient = PatientResponse(patient=rq, id = app.count)
    app.count += 1
    return patient