from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import restaurant_manager as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def manager_request():
    return SimpleNamespace(
        name="Taylor Morgan",
        email="taylor@example.com"
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_manager_success(db_session, manager_request, mocker):
    created_manager = mocker.Mock()
    created_manager.manager_id = 1
    created_manager.name = "Taylor Morgan"
    created_manager.email = "taylor@example.com"

    manager_constructor = mocker.patch(
        "api.controllers.restaurant_manager.model.RestaurantManager",
        return_value=created_manager
    )

    result = controller.create(db=db_session, request=manager_request)

    manager_constructor.assert_called_once_with(
        name="Taylor Morgan",
        email="taylor@example.com"
    )
    db_session.add.assert_called_once_with(created_manager)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_manager)

    assert result == created_manager
    assert result.manager_id == 1
    assert result.name == "Taylor Morgan"
    assert result.email == "taylor@example.com"


def test_create_manager_database_error(db_session, manager_request, mocker):
    fake_manager = mocker.Mock()

    mocker.patch(
        "api.controllers.restaurant_manager.model.RestaurantManager",
        return_value=fake_manager
    )

    db_session.add.side_effect = database_error(
        "Unable to create manager"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(db=db_session, request=manager_request)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create manager"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_managers_success(db_session, mocker):
    manager_one = mocker.Mock(manager_id=1)
    manager_two = mocker.Mock(manager_id=2)
    expected_managers = [manager_one, manager_two]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_managers

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.RestaurantManager
    )
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_managers
    assert len(result) == 2


def test_read_all_managers_empty(db_session):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_managers_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read managers"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read managers"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_manager_success(db_session, mocker):
    expected_manager = mocker.Mock()
    expected_manager.manager_id = 3
    expected_manager.name = "Jordan Lee"
    expected_manager.email = "jordan@example.com"

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_manager

    result = controller.read_one(
        db=db_session,
        manager_id=3
    )

    db_session.query.assert_called_once_with(
        controller.model.RestaurantManager
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_manager
    assert result.manager_id == 3
    assert result.name == "Jordan Lee"


def test_read_one_manager_not_found(db_session):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            manager_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Manager not found"


def test_read_one_manager_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read manager"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            manager_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read manager"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_manager_success(db_session, mocker):
    existing_manager = mocker.Mock()
    existing_manager.manager_id = 1
    existing_manager.name = "Taylor Morgan"
    existing_manager.email = "taylor@example.com"

    request = mocker.Mock()
    request.model_dump.return_value = {
        "name": "Taylor Smith",
        "email": "taylor.smith@example.com"
    }

    mocker.patch(
        "api.controllers.restaurant_manager.read_one",
        return_value=existing_manager
    )

    result = controller.update(
        db=db_session,
        manager_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_manager)

    assert result == existing_manager
    assert result.name == "Taylor Smith"
    assert result.email == "taylor.smith@example.com"


def test_update_manager_not_found(db_session, mocker):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.restaurant_manager.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            manager_id=999,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Manager not found"
    db_session.commit.assert_not_called()


def test_update_manager_database_error(db_session, mocker):
    existing_manager = mocker.Mock(
        manager_id=1,
        name="Taylor Morgan",
        email="taylor@example.com"
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "email": "updated@example.com"
    }

    mocker.patch(
        "api.controllers.restaurant_manager.read_one",
        return_value=existing_manager
    )

    db_session.commit.side_effect = database_error(
        "Unable to update manager"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            manager_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update manager"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_manager_success(db_session, mocker):
    existing_manager = mocker.Mock(manager_id=1)

    mocker.patch(
        "api.controllers.restaurant_manager.read_one",
        return_value=existing_manager
    )

    response = controller.delete(
        db=db_session,
        manager_id=1
    )

    db_session.delete.assert_called_once_with(existing_manager)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_manager_not_found(db_session, mocker):
    mocker.patch(
        "api.controllers.restaurant_manager.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            manager_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Manager not found"
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_manager_database_error(db_session, mocker):
    existing_manager = mocker.Mock(manager_id=1)

    mocker.patch(
        "api.controllers.restaurant_manager.read_one",
        return_value=existing_manager
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete manager"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            manager_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete manager"
    db_session.rollback.assert_called_once()