from collections.abc import Generator
from contextlib import contextmanager
from datetime import date

import connexion  # type: ignore
import connexion.lifecycle  # type: ignore
import pydantic
from flask import g
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend_engineer_interview.models import Application, Employee


class PydanticBaseModel(pydantic.BaseModel):
    model_config = {"from_attributes": True}


def construct_error_message(e: pydantic.ValidationError) -> str:
    error_messages = []
    separator = ";"

    for error in e.errors():
        if error["type"] == "missing":
            missing_field = error["loc"][-1]
            error_messages.append(f"{missing_field} is missing")
    
    if len(error_messages) > 0:
        return separator.join(error_messages)
    
    return ""


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Get a plain SQLAlchemy Session."""
    session: Session | None = g.get("db")
    if session is None:
        raise Exception("No database session available in application context")

    yield session


def get_request() -> connexion.lifecycle.ConnexionRequest:
    return connexion.request  # type: ignore[return-value]


def status() -> tuple[dict, int, dict]:
    with db_session() as session:
        session.execute(text("SELECT 1;")).one()
        return ({"status": "up"}, 200, {})


class EmployeeResponse(PydanticBaseModel):
    model_config = {"from_attributes": True}

    id: int
    first_name: str
    last_name: str
    date_of_birth: date


def get_employee(id: int) -> tuple[dict, int, dict]:
    with db_session() as session:
        employee = session.query(Employee).filter(Employee.id == id).one_or_none()

        if not employee:
            return ({"message": "No such employee"}, 404, {})
        return (EmployeeResponse.model_validate(employee).model_dump(), 200, {})


class PatchEmployeeRequest(PydanticBaseModel):
    first_name: str | None
    last_name: str | None


def patch_employee(id: int, body: dict) -> tuple[dict, int, dict]:
    with db_session() as session:
        employee: Employee | None = session.query(Employee).filter(Employee.id == id).one_or_none()
        if not employee:
            return ({"message": "No such employee"}, 404, {})

        try:
            request_body = PatchEmployeeRequest.model_validate(body)
            if request_body.first_name is not None:
                employee.first_name = request_body.first_name

            if request_body.last_name is not None:
                employee.last_name = request_body.last_name

            session.flush()

            return ({}, 204, {})
        except pydantic.ValidationError:
            if "first_name" in body and body["first_name"] == "":
                return ({"message": "first_name cannot be blank"}, 400, {})

            if "last_name" in body and body["last_name"] == "":
                return ({"message": "last_name cannot be blank"}, 400, {})

            return ({"message": "request not valid"}, 400, {})


class PostApplicationRequest(PydanticBaseModel):
    leave_start_date: date
    leave_end_date: date
    employee_id: int


class ApplicationResponse(PydanticBaseModel):
    model_config = {"from_attributes": True}

    id: int
    leave_start_date: date
    leave_end_date: date
    employee_id: int
    employee: EmployeeResponse


def post_application(body: dict) -> tuple[dict, int, dict]:
    with db_session() as session:
        try:
            request_body = PostApplicationRequest.model_validate(body)

            employee: Employee | None = session.query(Employee).filter(Employee.id == body["employee_id"]).one_or_none()
            if not employee:
                return ({"message": "No such employee"}, 404, {})

            new_application = Application(
                employee_id = employee.id,
                leave_start_date = request_body.leave_start_date,
                leave_end_date = request_body.leave_end_date,
                employee = employee
            )
            
            session.add(new_application)
            session.flush()

            return (ApplicationResponse.model_validate(new_application).model_dump(), 200, {})
        except pydantic.ValidationError as e:
            error_message = construct_error_message(e)

            if error_message != "":
                return ({"message": error_message}, 400, {})
            
            return ({"message": "request not valid"}, 400, {})


def search_application() -> None:
    """
    Returns a list of applications.  Can provide an employee id, first name or last name
    to filter the results
    """

    pass
