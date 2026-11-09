import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Employee Service")

EMPLOYEES_FILE = Path(__file__).resolve().parent.parent / "config" / "employees.json"


class Employee(BaseModel):
    name: str
    salary: float = Field(gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value


def read_employees():
    with open(EMPLOYEES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_employees(employees):
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as file:
        json.dump(employees, file, indent=4)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/employees")
def get_employees():
    return read_employees()


@app.get("/")
def home():
    return {"message": "Welcome to Employee Service"}


@app.get("/employees/{name}")
def get_employee(name: str):
    employees = read_employees()

    for employee in employees:
        if employee["name"].lower() == name.lower():
            return employee

    raise HTTPException(status_code=404, detail="Employee not found")


@app.post("/employees", status_code=201)
def create_employee(employee: Employee):
    employees = read_employees()

    for existing in employees:
        if existing["name"].lower() == employee.name.lower():
            raise HTTPException(status_code=409, detail="Employee already exists")

    employees.append(employee.model_dump())
    save_employees(employees)

    return employee
