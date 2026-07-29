from decimal import Decimal

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import menu_item_inventory as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def link_request(mocker):
    request = mocker.Mock()
    request.model_dump.return_value = {
        "item_id": 1,
        "ingredient_id": 2,
        "quantity_required": Decimal("1.50")
    }
    return request


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_link_success(
    db_session,
    link_request,
    mocker
):
    created_link = mocker.Mock()
    created_link.item_id = 1
    created_link.ingredient_id = 2
    created_link.quantity_required = Decimal("1.50")

    constructor = mocker.patch(
        "api.controllers.menu_item_inventory.model.MenuItemInventory",
        return_value=created_link
    )

    result = controller.create(
        db=db_session,
        request=link_request
    )

    link_request.model_dump.assert_called_once_with()

    constructor.assert_called_once_with(
        item_id=1,
        ingredient_id=2,
        quantity_required=Decimal("1.50")
    )

    db_session.add.assert_called_once_with(created_link)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_link)

    assert result == created_link
    assert result.item_id == 1
    assert result.ingredient_id == 2
    assert result.quantity_required == Decimal("1.50")


def test_create_link_database_error(
    db_session,
    link_request,
    mocker
):
    fake_link = mocker.Mock()

    mocker.patch(
        "api.controllers.menu_item_inventory.model.MenuItemInventory",
        return_value=fake_link
    )

    db_session.add.side_effect = database_error(
        "Unable to create menu item inventory link"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=link_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == (
        "Unable to create menu item inventory link"
    )
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_links_success(
    db_session,
    mocker
):
    link_one = mocker.Mock(item_id=1, ingredient_id=1)
    link_two = mocker.Mock(item_id=1, ingredient_id=2)
    expected_links = [link_one, link_two]

    query = db_session.query.return_value
    query.all.return_value = expected_links

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.MenuItemInventory
    )
    query.all.assert_called_once()

    assert result == expected_links
    assert len(result) == 2


def test_read_all_links_empty(
    db_session
):
    query = db_session.query.return_value
    query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_links_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read menu item inventory links"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == (
        "Unable to read menu item inventory links"
    )


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_link_success(
    db_session,
    mocker
):
    expected_link = mocker.Mock()
    expected_link.item_id = 1
    expected_link.ingredient_id = 2
    expected_link.quantity_required = Decimal("1.50")

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_link

    result = controller.read_one(
        db=db_session,
        item_id=1,
        ingredient_id=2
    )

    db_session.query.assert_called_once_with(
        controller.model.MenuItemInventory
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_link
    assert result.item_id == 1
    assert result.ingredient_id == 2


def test_read_one_link_not_found(
    db_session
):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            item_id=9,
            ingredient_id=8
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == (
        "Link between menu item 9 and ingredient 8 not found"
    )


def test_read_one_link_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read menu item inventory link"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            item_id=1,
            ingredient_id=2
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == (
        "Unable to read menu item inventory link"
    )


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_link_success(
    db_session,
    mocker
):
    existing_link = mocker.Mock()
    existing_link.item_id = 1
    existing_link.ingredient_id = 2
    existing_link.quantity_required = Decimal("1.50")

    request = mocker.Mock()
    request.model_dump.return_value = {
        "quantity_required": Decimal("2.00")
    }

    mocker.patch(
        "api.controllers.menu_item_inventory.read_one",
        return_value=existing_link
    )

    result = controller.update(
        db=db_session,
        item_id=1,
        ingredient_id=2,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_link)

    assert result == existing_link
    assert result.quantity_required == Decimal("2.00")


def test_update_link_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.menu_item_inventory.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link between menu item 9 and ingredient 8 not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            item_id=9,
            ingredient_id=8,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == (
        "Link between menu item 9 and ingredient 8 not found"
    )
    db_session.commit.assert_not_called()


def test_update_link_database_error(
    db_session,
    mocker
):
    existing_link = mocker.Mock(
        item_id=1,
        ingredient_id=2,
        quantity_required=Decimal("1.50")
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "quantity_required": Decimal("2.00")
    }

    mocker.patch(
        "api.controllers.menu_item_inventory.read_one",
        return_value=existing_link
    )

    db_session.commit.side_effect = database_error(
        "Unable to update menu item inventory link"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            item_id=1,
            ingredient_id=2,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == (
        "Unable to update menu item inventory link"
    )
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_link_success(
    db_session,
    mocker
):
    existing_link = mocker.Mock(
        item_id=1,
        ingredient_id=2
    )

    mocker.patch(
        "api.controllers.menu_item_inventory.read_one",
        return_value=existing_link
    )

    response = controller.delete(
        db=db_session,
        item_id=1,
        ingredient_id=2
    )

    db_session.delete.assert_called_once_with(existing_link)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_link_not_found(
    db_session,
    mocker
):
    mocker.patch(
        "api.controllers.menu_item_inventory.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link between menu item 9 and ingredient 8 not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            item_id=9,
            ingredient_id=8
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == (
        "Link between menu item 9 and ingredient 8 not found"
    )
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_link_database_error(
    db_session,
    mocker
):
    existing_link = mocker.Mock(
        item_id=1,
        ingredient_id=2
    )

    mocker.patch(
        "api.controllers.menu_item_inventory.read_one",
        return_value=existing_link
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete menu item inventory link"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            item_id=1,
            ingredient_id=2
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == (
        "Unable to delete menu item inventory link"
    )
    db_session.rollback.assert_called_once()