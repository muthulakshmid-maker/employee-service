import json

import pytest
from fastapi.testclient import TestClient

import src.main as main
from src.main import app

client = TestClient(app)


@pytest.fixture
def employee_file(tmp_path, monkeypatch):
    file_path = tmp_path / "employees.json"

    employees = [
        {"name": "Ravi", "salary": 30000},
        {"name": "Priya", "salary": 45000},
    ]

    file_path.write_text(json.dumps(employees), encoding="utf-8")

    monkeypatch.setattr(main, "EMPLOYEES_FILE", file_path)

    return file_path


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_employees(employee_file):
    response = client.get("/employees")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_employee(employee_file):
    response = client.get("/employees/Ravi")

    assert response.status_code == 200
    assert response.json()["name"] == "Ravi"


def test_employee_not_found(employee_file):
    response = client.get("/employees/Unknown")

    assert response.status_code == 404


def test_invalid_salary(employee_file):
    response = client.post("/employees", json={"name": "Kumar", "salary": -5})

    assert response.status_code == 422


def test_empty_name(employee_file):
    response = client.post("/employees", json={"name": "", "salary": 30000})

    assert response.status_code == 422


def test_create_employee(employee_file):
    response = client.post("/employees", json={"name": "Kumar", "salary": 50000})

    assert response.status_code == 201
    assert response.json()["name"] == "Kumar"

    employees = json.loads(employee_file.read_text())

    assert len(employees) == 3
