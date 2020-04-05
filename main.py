from typing import Dict

from fastapi import FastAPI

from pydantic import BaseModel


app = FastAPI()


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

class PatientRequest(BaseModel):
    name: str
    surename: str

class PatientResponse(BaseModel):
    id: int
    patient: Dict
@app.post("/patient", response_model=PatientResponse)
def new_patient(rq: PatientRequest):
    new_patient.id += 1
    return PatientResponse(patient=rq.dict(), id = new_patient.id)
new_patient.id = -1