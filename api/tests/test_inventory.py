from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import inventory as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def inventory_request(mocker):
    request = mocker.Mock()
    request.model_dump.return_value = {
        "ingredient_name": "Tomatoes",
        "quantity": 50,
        "minimum_quantity": 10,
        "maintained_by_manager_id": 1
    }
    return request


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error



# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_inventory_success(
    db_session,
    inventory_request,
    mocker
):
    created_inventory = mocker.Mock()
    created_inventory.ingredient_id = 1
    created_inventory.ingredient_name = "Tomatoes"

    inventory_constructor = mocker.patch(
        "api.controllers.inventory.model.Inventory",
        return_value=created_inventory
    )

    inventory_request.model_dump = mocker.Mock(
        return_value={
            "ingredient_name": "Tomatoes",
            "quantity": 50,
            "minimum_quantity": 10,
            "maintained_by_manager_id": 1
        }
    )

    result = controller.create(
        db=db_session,
        request=inventory_request
    )

    inventory_request.model_dump.assert_called_once_with()

    inventory_constructor.assert_called_once_with(
        ingredient_name="Tomatoes",
        quantity=50,
        minimum_quantity=10,
        maintained_by_manager_id=1
    )

    db_session.add.assert_called_once_with(created_inventory)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_inventory)

    assert result == created_inventory
    assert result.ingredient_id == 1
    assert result.ingredient_name == "Tomatoes"


def test_create_inventory_database_error(
    db_session,
    inventory_request,
    mocker
):
    fake_inventory = mocker.Mock()

    inventory_request.model_dump = mocker.Mock(
        return_value={
            "ingredient_name": "Tomatoes",
            "quantity": 50,
            "minimum_quantity": 10,
            "maintained_by_manager_id": 1
        }
    )

    mocker.patch(
        "api.controllers.inventory.model.Inventory",
        return_value=fake_inventory
    )

    db_session.add.side_effect = database_error(
        "Unable to create inventory"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=inventory_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create inventory"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_inventory_success(db_session, mocker):
    expected = [mocker.Mock(), mocker.Mock()]

    query = db_session.query.return_value
    ordered = query.order_by.return_value
    ordered.all.return_value = expected

    result = controller.read_all(db=db_session)

    assert result == expected


def test_read_all_inventory_empty(db_session):
    query = db_session.query.return_value
    ordered = query.order_by.return_value
    ordered.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_inventory_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read inventory"
    )

    with pytest.raises(HTTPException):
        controller.read_all(db=db_session)


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_inventory_success(db_session, mocker):
    inventory = mocker.Mock()

    query = db_session.query.return_value
    filtered = query.filter.return_value
    filtered.first.return_value = inventory

    result = controller.read_one(
        db=db_session,
        ingredient_id=1
    )

    assert result == inventory


def test_read_one_inventory_not_found(db_session):
    query = db_session.query.return_value
    filtered = query.filter.return_value
    filtered.first.return_value = None

    with pytest.raises(HTTPException):
        controller.read_one(db=db_session, ingredient_id=999)


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_inventory_success(db_session, mocker):
    inventory = mocker.Mock()

    request = mocker.Mock()
    request.model_dump.return_value = {
        "quantity": 75
    }

    mocker.patch(
        "api.controllers.inventory.read_one",
        return_value=inventory
    )

    result = controller.update(
        db=db_session,
        ingredient_id=1,
        request=request
    )

    assert result == inventory

    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(inventory)


def test_update_inventory_not_found(db_session, mocker):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.inventory.read_one",
        side_effect=HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )
    )

    with pytest.raises(HTTPException):
        controller.update(
            db=db_session,
            ingredient_id=999,
            request=request
        )


def test_update_inventory_database_error(
    db_session,
    mocker
):
    inventory = mocker.Mock()

    request = mocker.Mock()
    request.model_dump.return_value = {
        "quantity": 10
    }

    mocker.patch(
        "api.controllers.inventory.read_one",
        return_value=inventory
    )

    db_session.commit.side_effect = database_error(
        "Unable to update inventory"
    )

    with pytest.raises(HTTPException):
        controller.update(
            db=db_session,
            ingredient_id=1,
            request=request
        )

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_inventory_success(db_session, mocker):
    inventory = mocker.Mock()

    mocker.patch(
        "api.controllers.inventory.read_one",
        return_value=inventory
    )

    response = controller.delete(
        db=db_session,
        ingredient_id=1
    )

    db_session.delete.assert_called_once_with(inventory)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_inventory_not_found(db_session, mocker):
    mocker.patch(
        "api.controllers.inventory.read_one",
        side_effect=HTTPException(
            status_code=404,
            detail="Inventory item not found"
        )
    )

    with pytest.raises(HTTPException):
        controller.delete(
            db=db_session,
            ingredient_id=999
        )


def test_delete_inventory_database_error(db_session, mocker):
    inventory = mocker.Mock()

    mocker.patch(
        "api.controllers.inventory.read_one",
        return_value=inventory
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete inventory"
    )

    with pytest.raises(HTTPException):
        controller.delete(
            db=db_session,
            ingredient_id=1
        )

    db_session.rollback.assert_called_once()