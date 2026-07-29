from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import orders as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def order_request():
    return SimpleNamespace(
        order_status="Pending",
        order_type="Takeout",
        total_price=Decimal("24.99"),
        estimated_time=20,
        promo_code=None,
        customer_id=1,
        employee_id=1
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_order_success(db_session, order_request, mocker):
    created_order = mocker.Mock()
    created_order.order_id = 1
    created_order.order_status = "Pending"

    order_constructor = mocker.patch(
        "api.controllers.orders.model.Order",
        return_value=created_order
    )

    result = controller.create(db=db_session, request=order_request)

    order_constructor.assert_called_once_with(
        order_status="Pending",
        order_type="Takeout",
        total_price=Decimal("24.99"),
        estimated_time=20,
        promo_code=None,
        customer_id=1,
        employee_id=1
    )

    db_session.add.assert_called_once_with(created_order)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_order)

    assert result == created_order
    assert result.order_id == 1
    assert result.order_status == "Pending"


def test_create_order_database_error(db_session, order_request, mocker):
    fake_order = mocker.Mock()

    mocker.patch(
        "api.controllers.orders.model.Order",
        return_value=fake_order
    )

    db_session.add.side_effect = database_error(
        "Unable to create order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(db=db_session, request=order_request)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create order"

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_orders_success(db_session, mocker):
    order_one = mocker.Mock(order_id=1)
    order_two = mocker.Mock(order_id=2)
    expected_orders = [order_one, order_two]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_orders

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(controller.model.Order)
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_orders
    assert len(result) == 2


def test_read_all_orders_empty(db_session):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_orders_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read orders"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read orders"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_order_success(db_session, mocker):
    expected_order = mocker.Mock()
    expected_order.order_id = 4
    expected_order.order_status = "Preparing"

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_order

    result = controller.read_one(db=db_session, order_id=4)

    db_session.query.assert_called_once_with(controller.model.Order)
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_order
    assert result.order_id == 4
    assert result.order_status == "Preparing"


def test_read_one_order_not_found(db_session):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(db=db_session, order_id=999)

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Order not found"


def test_read_one_order_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(db=db_session, order_id=1)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read order"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_order_success(db_session, mocker):
    existing_order = mocker.Mock()
    existing_order.order_id = 1
    existing_order.order_status = "Pending"
    existing_order.total_price = Decimal("24.99")

    request = mocker.Mock()
    request.model_dump.return_value = {
        "order_status": "Completed",
        "total_price": Decimal("29.99")
    }

    mocker.patch(
        "api.controllers.orders.read_one",
        return_value=existing_order
    )

    result = controller.update(
        db=db_session,
        order_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(exclude_unset=True)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_order)

    assert result == existing_order
    assert result.order_status == "Completed"
    assert result.total_price == Decimal("29.99")


def test_update_order_not_found(db_session, mocker):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.orders.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            order_id=999,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Order not found"

    db_session.commit.assert_not_called()


def test_update_order_database_error(db_session, mocker):
    existing_order = mocker.Mock()

    request = mocker.Mock()
    request.model_dump.return_value = {
        "order_status": "Completed"
    }

    mocker.patch(
        "api.controllers.orders.read_one",
        return_value=existing_order
    )

    db_session.commit.side_effect = database_error(
        "Unable to update order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            order_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update order"

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_order_success(db_session, mocker):
    existing_order = mocker.Mock()
    existing_order.order_id = 1

    mocker.patch(
        "api.controllers.orders.read_one",
        return_value=existing_order
    )

    response = controller.delete(
        db=db_session,
        order_id=1
    )

    db_session.delete.assert_called_once_with(existing_order)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_order_not_found(db_session, mocker):
    mocker.patch(
        "api.controllers.orders.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            order_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Order not found"

    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_order_database_error(db_session, mocker):
    existing_order = mocker.Mock()
    existing_order.order_id = 1

    mocker.patch(
        "api.controllers.orders.read_one",
        return_value=existing_order
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete order"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            order_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete order"

    db_session.rollback.assert_called_once()