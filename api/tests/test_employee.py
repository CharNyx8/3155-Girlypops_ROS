from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import employee as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def employee_request():
    return SimpleNamespace(
        name="Alex Morgan",
        role="Server"
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_employee_success(
    db_session,
    employee_request,
    mocker
):
    created_employee = mocker.Mock()
    created_employee.employee_id = 1
    created_employee.name = "Alex Morgan"
    created_employee.role = "Server"

    employee_constructor = mocker.patch(
        "api.controllers.employee.model.RestaurantEmployee",
        return_value=created_employee
    )

    result = controller.create(
        db=db_session,
        request=employee_request
    )

    employee_constructor.assert_called_once_with(
        name="Alex Morgan",
        role="Server"
    )

    db_session.add.assert_called_once_with(created_employee)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_employee)

    assert result == created_employee
    assert result.employee_id == 1
    assert result.name == "Alex Morgan"
    assert result.role == "Server"


def test_create_employee_database_error(
    db_session,
    employee_request,
    mocker
):
    fake_employee = mocker.Mock()

    mocker.patch(
        "api.controllers.employee.model.RestaurantEmployee",
        return_value=fake_employee
    )

    db_session.add.side_effect = database_error(
        "Unable to create employee"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=employee_request
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to create employee"
    )

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_employees_success(
    db_session,
    mocker
):
    employee_one = mocker.Mock(employee_id=1)
    employee_two = mocker.Mock(employee_id=2)

    expected_employees = [
        employee_one,
        employee_two
    ]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_employees

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.RestaurantEmployee
    )
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_employees
    assert len(result) == 2


def test_read_all_employees_empty(
    db_session
):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_employees_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read employees"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to read employees"
    )


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_employee_success(
    db_session,
    mocker
):
    expected_employee = mocker.Mock()
    expected_employee.employee_id = 3
    expected_employee.name = "Jordan Lee"
    expected_employee.role = "Cook"

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_employee

    result = controller.read_one(
        db=db_session,
        employee_id=3
    )

    db_session.query.assert_called_once_with(
        controller.model.RestaurantEmployee
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_employee
    assert result.employee_id == 3
    assert result.name == "Jordan Lee"
    assert result.role == "Cook"


def test_read_one_employee_not_found(
    db_session
):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            employee_id=999
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Employee not found"


def test_read_one_employee_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read employee"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            employee_id=1
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to read employee"
    )


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_employee_success(
    db_session,
    mocker
):
    existing_employee = mocker.Mock()
    existing_employee.employee_id = 1
    existing_employee.name = "Alex Morgan"
    existing_employee.role = "Server"

    request = mocker.Mock()
    request.model_dump.return_value = {
        "name": "Alexandra Morgan",
        "role": "Shift Lead"
    }

    mocker.patch(
        "api.controllers.employee.read_one",
        return_value=existing_employee
    )

    result = controller.update(
        db=db_session,
        employee_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )

    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(
        existing_employee
    )

    assert result == existing_employee
    assert result.name == "Alexandra Morgan"
    assert result.role == "Shift Lead"


def test_update_employee_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.employee.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            employee_id=999,
            request=request
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Employee not found"

    db_session.commit.assert_not_called()


def test_update_employee_database_error(
    db_session,
    mocker
):
    existing_employee = mocker.Mock(
        employee_id=1,
        name="Alex Morgan",
        role="Server"
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "role": "Shift Lead"
    }

    mocker.patch(
        "api.controllers.employee.read_one",
        return_value=existing_employee
    )

    db_session.commit.side_effect = database_error(
        "Unable to update employee"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            employee_id=1,
            request=request
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to update employee"
    )

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_employee_success(
    db_session,
    mocker
):
    existing_employee = mocker.Mock(
        employee_id=1
    )

    mocker.patch(
        "api.controllers.employee.read_one",
        return_value=existing_employee
    )

    response = controller.delete(
        db=db_session,
        employee_id=1
    )

    db_session.delete.assert_called_once_with(
        existing_employee
    )
    db_session.commit.assert_called_once()

    assert response.status_code == (
        status.HTTP_204_NO_CONTENT
    )


def test_delete_employee_not_found(
    db_session,
    mocker
):
    mocker.patch(
        "api.controllers.employee.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            employee_id=999
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Employee not found"

    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_employee_database_error(
    db_session,
    mocker
):
    existing_employee = mocker.Mock(
        employee_id=1
    )

    mocker.patch(
        "api.controllers.employee.read_one",
        return_value=existing_employee
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete employee"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            employee_id=1
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to delete employee"
    )

    db_session.rollback.assert_called_once()