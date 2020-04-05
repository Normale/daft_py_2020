  
from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World during the coronavirus pandemic!"} 


def test_methods():
    response = client.get(f"/method")
    assert response.status_code == 200
    assert response.json() == {'method': "GET"}
    response = client.post(f"/method")
    assert response.status_code == 200
    assert response.json() == {'method': "POST"}
    response = client.put(f"/method")
    assert response.status_code == 200
    assert response.json() == {'method': "PUT"}


@pytest.mark.parametrize("name", ['Zenek', 'Marek', 'Alojzy Niezdąży'])
@pytest.mark.parametrize("surename", ['Zenekx', 'Marekx', 'Alojzy Niezdyx'])
def test_patients(name, surename):
    response = client.post("/patient", json={"name": f"{name}", 
                                            "surename": f"{surename}"})
    assert response.json() == {"id": test_patients.callCount, "patient": {"name": f"{name}", 
                                                                "surename": f"{surename}"}}
    test_patients.callCount += 1

test_patients.callCount = 0