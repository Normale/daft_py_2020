from typing import Dict

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel


app = FastAPI()
app.count: int = 0
app.patients: list = []


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
    app.patients.append(rq)
    patient = PatientResponse(id = app.count, patient=rq)
    app.count += 1
    return patient

@app.get("/patient/{id}")
def receive_patient(id: int):
    if id < len(app.patients):
        return app.patients[id-1]
    else:
        raise HTTPException(status_code=204, detail="Index not found")