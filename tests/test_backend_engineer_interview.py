from typing import Self

from connexion.apps.abstract import TestClient  # type: ignore

from backend_engineer_interview import __version__


class TestGetEmployee:
    def test_get_employee_endpoint_200(self: Self, test_client: TestClient) -> None:
        response = test_client.get("/v1/employee/1")
        assert response.status_code == 200
        employee_data = response.json()
        assert employee_data["id"] == 1
        assert employee_data["first_name"] == "John"
        assert employee_data["last_name"] == "Lennon"
        assert employee_data["date_of_birth"] == "1940-10-04"
        assert "secret" not in employee_data

    def test_get_employee_endpoint_404(self: Self, test_client: TestClient) -> None:
        response = test_client.get("/v1/employee/99")
        assert response.status_code == 404
        assert response.json()["message"] == "No such employee"


class TestPatchEmployee:
    def test_patch_employee_valid(self: Self, test_client: TestClient) -> None:
        current_response = test_client.get("/v1/employee/2")
        assert current_response.json()["first_name"] == "Rino"
        assert current_response.json()["last_name"] == "Star"
        patch_response = test_client.patch(
            "/v1/employee/2", json={"first_name": "Ringo", "last_name": "Starr"}
        )
        assert patch_response.status_code == 204
        updated_response = test_client.get("/v1/employee/2")
        assert updated_response.json()["first_name"] == "Ringo"
        assert updated_response.json()["last_name"] == "Starr"

    def test_patch_employee_endpoint_404(self: Self, test_client: TestClient) -> None:
        response = test_client.patch(
            "/v1/employee/99", json={"first_name": "Ringo", "last_name": "Starr"}
        )
        assert response.status_code == 404
        assert response.json()["message"] == "No such employee"

    def test_patch_employee_invalid(self: Self, test_client: TestClient) -> None:
        patch_response = test_client.patch("/v1/employee/10", json={"last_name": ""})
        assert patch_response.status_code == 400
        assert patch_response.json()["message"] == "last_name cannot be blank"


class TestPostApplication:
    def test_post_application_valid(self: Self, test_client: TestClient) -> None:
        application_response = test_client.post(
            "/v1/application",
            json={
                "leave_start_date": "2021-01-01",
                "leave_end_date": "2021-02-01",
                "employee_id": 1,
            },
        )
        assert application_response.status_code == 200
        application = application_response.json()
        assert application["leave_start_date"] == "2021-01-01"
        assert application["leave_end_date"] == "2021-02-01"
        assert application["employee"]["first_name"] == "John"
        assert application["id"] is not None

    def test_post_application_invalid(self: Self, test_client: TestClient) -> None:
        application_response = test_client.post(
            "/v1/application",
            json={
                "employee_id": 1,
            },
        )
        assert application_response.status_code == 400
        assert (
            application_response.json()["message"]
            == "leave_start_date is missing;leave_end_date is missing"
        )
    
    def test_post_application_404(self: Self, test_client: TestClient) -> None:
        application_response = test_client.post(
            "/v1/application",
            json={
                "leave_start_date": "2021-01-01",
                "leave_end_date": "2021-02-01",
                "employee_id": 123,
            },
        )
        assert application_response.status_code == 400
        assert (
            application_response.json()["message"]
            == "No such employee"
        )


def test_version() -> None:
    assert __version__ == "0.1.0"
