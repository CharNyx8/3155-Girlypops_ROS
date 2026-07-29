from decimal import Decimal

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import menu_item as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def menu_item_request(mocker):
    request = mocker.Mock()
    request.model_dump.return_value = {
        "item_name": "Classic Burger",
        "description": "Beef burger with lettuce and tomato",
        "price": Decimal("12.99"),
        "category": "Entree",
        "dietary_type": None,
        "is_available": True,
        "created_by_manager_id": 1
    }
    return request


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_menu_item_success(
    db_session,
    menu_item_request,
    mocker
):
    created_item = mocker.Mock()
    created_item.item_id = 1
    created_item.item_name = "Classic Burger"
    created_item.price = Decimal("12.99")
    created_item.is_available = True

    constructor = mocker.patch(
        "api.controllers.menu_item.model.MenuItem",
        return_value=created_item
    )

    result = controller.create(
        db=db_session,
        request=menu_item_request
    )

    menu_item_request.model_dump.assert_called_once_with()

    constructor.assert_called_once_with(
        item_name="Classic Burger",
        description="Beef burger with lettuce and tomato",
        price=Decimal("12.99"),
        category="Entree",
        dietary_type=None,
        is_available=True,
        created_by_manager_id=1
    )

    db_session.add.assert_called_once_with(created_item)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_item)

    assert result == created_item
    assert result.item_id == 1
    assert result.item_name == "Classic Burger"
    assert result.price == Decimal("12.99")
    assert result.is_available is True


def test_create_menu_item_database_error(
    db_session,
    menu_item_request,
    mocker
):
    fake_item = mocker.Mock()

    mocker.patch(
        "api.controllers.menu_item.model.MenuItem",
        return_value=fake_item
    )

    db_session.add.side_effect = database_error(
        "Unable to create menu item"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=menu_item_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create menu item"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_menu_items_success(
    db_session,
    mocker
):
    item_one = mocker.Mock(item_id=1, item_name="Burger")
    item_two = mocker.Mock(item_id=2, item_name="Fries")
    expected_items = [item_one, item_two]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_items

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.MenuItem
    )
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_items
    assert len(result) == 2


def test_read_all_menu_items_empty(
    db_session
):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_menu_items_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read menu items"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read menu items"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_menu_item_success(
    db_session,
    mocker
):
    expected_item = mocker.Mock()
    expected_item.item_id = 3
    expected_item.item_name = "Garden Salad"
    expected_item.price = Decimal("9.99")
    expected_item.is_available = True

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_item

    result = controller.read_one(
        db=db_session,
        item_id=3
    )

    db_session.query.assert_called_once_with(
        controller.model.MenuItem
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_item
    assert result.item_id == 3
    assert result.item_name == "Garden Salad"
    assert result.price == Decimal("9.99")


def test_read_one_menu_item_not_found(
    db_session
):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            item_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Menu item with id 999 not found"


def test_read_one_menu_item_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read menu item"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            item_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read menu item"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_menu_item_success(
    db_session,
    mocker
):
    existing_item = mocker.Mock()
    existing_item.item_id = 1
    existing_item.item_name = "Classic Burger"
    existing_item.price = Decimal("12.99")
    existing_item.is_available = True

    request = mocker.Mock()
    request.model_dump.return_value = {
        "item_name": "Deluxe Burger",
        "price": Decimal("14.99"),
        "is_available": False
    }

    mocker.patch(
        "api.controllers.menu_item.read_one",
        return_value=existing_item
    )

    result = controller.update(
        db=db_session,
        item_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_item)

    assert result == existing_item
    assert result.item_name == "Deluxe Burger"
    assert result.price == Decimal("14.99")
    assert result.is_available is False


def test_update_menu_item_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.menu_item.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item with id 999 not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            item_id=999,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Menu item with id 999 not found"
    db_session.commit.assert_not_called()


def test_update_menu_item_database_error(
    db_session,
    mocker
):
    existing_item = mocker.Mock(
        item_id=1,
        item_name="Classic Burger",
        price=Decimal("12.99")
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "price": Decimal("15.99")
    }

    mocker.patch(
        "api.controllers.menu_item.read_one",
        return_value=existing_item
    )

    db_session.commit.side_effect = database_error(
        "Unable to update menu item"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            item_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update menu item"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_menu_item_success(
    db_session,
    mocker
):
    existing_item = mocker.Mock(item_id=1)

    mocker.patch(
        "api.controllers.menu_item.read_one",
        return_value=existing_item
    )

    response = controller.delete(
        db=db_session,
        item_id=1
    )

    db_session.delete.assert_called_once_with(existing_item)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_menu_item_not_found(
    db_session,
    mocker
):
    mocker.patch(
        "api.controllers.menu_item.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item with id 999 not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            item_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Menu item with id 999 not found"
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_menu_item_database_error(
    db_session,
    mocker
):
    existing_item = mocker.Mock(item_id=1)

    mocker.patch(
        "api.controllers.menu_item.read_one",
        return_value=existing_item
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete menu item"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            item_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete menu item"
    db_session.rollback.assert_called_once()