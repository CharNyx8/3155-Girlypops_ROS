from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import orders as controller


@pytest.fixture
def db_session(mocker):
    """Create a fake SQLAlchemy database session."""
    return mocker.Mock()


@pytest.fixture
def order_request():
    """Create reusable sample data for a new order."""
    return SimpleNamespace(
        orderStatus="Pending",
        orderType="Takeout",
        totalPrice=Decimal("24.99"),
        estimatedTime=20,
        promoCode=None,
        customerID=1,
        employeeID=1
    )


def database_error(message):
    """
    Create a SQLAlchemyError with the 'orig' attribute format
    expected by the current controller.
    """
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_order_success(
    db_session,
    order_request,
    mocker
):
    created_order = mocker.Mock()
    created_order.orderID = 1
    created_order.orderStatus = "Pending"

    order_constructor = mocker.patch(
        "api.controllers.orders.model.Order",
        return_value=created_order
    )

    result = controller.create(
        db=db_session,
        request=order_request
    )

    order_constructor.assert_called_once_with(
        orderStatus="Pending",
        orderType="Takeout",
        totalPrice=Decimal("24.99"),
        estimatedTime=20,
        promoCode=None,
        customerID=1,
        employeeID=1
    )

    db_session.add.assert_called_once_with(created_order)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_order)

    assert result == created_order
    assert result.orderID == 1


def test_create_order_database_error(
    db_session,
    order_request,
    mocker
):
    fake_order = mocker.Mock()

    mocker.patch(
        "api.controllers.orders.model.Order",
        return_value=fake_order
    )

    db_session.add.side_effect = database_error(
        "Unable to create order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=order_request
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == "Unable to create order"


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_orders_success(
    db_session,
    mocker
):
    order_one = mocker.Mock()
    order_one.orderID = 1

    order_two = mocker.Mock()
    order_two.orderID = 2

    expected_orders = [order_one, order_two]

    query = db_session.query.return_value
    query.all.return_value = expected_orders

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.Order
    )
    query.all.assert_called_once()

    assert result == expected_orders
    assert len(result) == 2


def test_read_all_orders_empty(
    db_session
):
    query = db_session.query.return_value
    query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_orders_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read orders"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == "Unable to read orders"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_order_success(
    db_session,
    mocker
):
    expected_order = mocker.Mock()
    expected_order.orderID = 4
    expected_order.orderStatus = "Preparing"

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_order

    result = controller.read_one(
        db=db_session,
        item_id=4
    )

    db_session.query.assert_called_once_with(
        controller.model.Order
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_order
    assert result.orderID == 4


def test_read_one_order_not_found(
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

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Id not found!"


def test_read_one_order_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            item_id=1
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == "Unable to read order"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_order_success(
    db_session,
    mocker
):
    existing_order = mocker.Mock()
    existing_order.orderID = 1
    existing_order.orderStatus = "Pending"

    updated_order = mocker.Mock()
    updated_order.orderID = 1
    updated_order.orderStatus = "Completed"

    request = mocker.Mock()
    request.dict.return_value = {
        "orderStatus": "Completed"
    }

    query = db_session.query.return_value
    item_query = query.filter.return_value

    item_query.first.side_effect = [
        existing_order,
        updated_order
    ]

    result = controller.update(
        db=db_session,
        item_id=1,
        request=request
    )

    request.dict.assert_called_once_with(
        exclude_unset=True
    )

    item_query.update.assert_called_once_with(
        {"orderStatus": "Completed"},
        synchronize_session=False
    )

    db_session.commit.assert_called_once()

    assert result == updated_order
    assert result.orderStatus == "Completed"


def test_update_order_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    query = db_session.query.return_value
    item_query = query.filter.return_value
    item_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            item_id=999,
            request=request
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Id not found!"

    item_query.update.assert_not_called()
    db_session.commit.assert_not_called()


def test_update_order_database_error(
    db_session,
    mocker
):
    existing_order = mocker.Mock()

    request = mocker.Mock()
    request.dict.return_value = {
        "orderStatus": "Completed"
    }

    query = db_session.query.return_value
    item_query = query.filter.return_value
    item_query.first.return_value = existing_order

    item_query.update.side_effect = database_error(
        "Unable to update order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            item_id=1,
            request=request
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == "Unable to update order"


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_order_success(
    db_session,
    mocker
):
    existing_order = mocker.Mock()
    existing_order.orderID = 1

    query = db_session.query.return_value
    item_query = query.filter.return_value
    item_query.first.return_value = existing_order

    response = controller.delete(
        db=db_session,
        item_id=1
    )

    item_query.delete.assert_called_once_with(
        synchronize_session=False
    )

    db_session.commit.assert_called_once()

    assert response.status_code == (
        status.HTTP_204_NO_CONTENT
    )


def test_delete_order_not_found(
    db_session
):
    query = db_session.query.return_value
    item_query = query.filter.return_value
    item_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            item_id=999
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Id not found!"

    item_query.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_order_database_error(
    db_session,
    mocker
):
    existing_order = mocker.Mock()

    query = db_session.query.return_value
    item_query = query.filter.return_value
    item_query.first.return_value = existing_order

    item_query.delete.side_effect = database_error(
        "Unable to delete order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            item_id=1
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == "Unable to delete order"