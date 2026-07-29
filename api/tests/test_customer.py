from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import customer as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def customer_request():
    return SimpleNamespace(
        name="Jamie Carter",
        email="jamie@example.com",
        phone="555-0100",
        has_account=True
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_customer_success(
    db_session,
    customer_request,
    mocker
):
    created_customer = mocker.Mock()
    created_customer.customer_id = 1
    created_customer.name = "Jamie Carter"
    created_customer.email = "jamie@example.com"
    created_customer.phone = "555-0100"
    created_customer.has_account = True

    customer_constructor = mocker.patch(
        "api.controllers.customer.model.Customer",
        return_value=created_customer
    )

    result = controller.create(
        db=db_session,
        request=customer_request
    )

    customer_constructor.assert_called_once_with(
        name="Jamie Carter",
        email="jamie@example.com",
        phone="555-0100",
        has_account=True
    )

    db_session.add.assert_called_once_with(created_customer)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_customer)

    assert result == created_customer
    assert result.customer_id == 1
    assert result.name == "Jamie Carter"
    assert result.email == "jamie@example.com"
    assert result.has_account is True


def test_create_customer_database_error(
    db_session,
    customer_request,
    mocker
):
    fake_customer = mocker.Mock()

    mocker.patch(
        "api.controllers.customer.model.Customer",
        return_value=fake_customer
    )

    db_session.add.side_effect = database_error(
        "Unable to create customer"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=customer_request
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to create customer"
    )

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_customers_success(
    db_session,
    mocker
):
    customer_one = mocker.Mock(customer_id=1)
    customer_two = mocker.Mock(customer_id=2)

    expected_customers = [
        customer_one,
        customer_two
    ]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_customers

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.Customer
    )
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_customers
    assert len(result) == 2


def test_read_all_customers_empty(
    db_session
):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_customers_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read customers"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to read customers"
    )


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_customer_success(
    db_session,
    mocker
):
    expected_customer = mocker.Mock()
    expected_customer.customer_id = 3
    expected_customer.name = "Morgan Lee"
    expected_customer.email = "morgan@example.com"
    expected_customer.phone = None
    expected_customer.has_account = False

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_customer

    result = controller.read_one(
        db=db_session,
        customer_id=3
    )

    db_session.query.assert_called_once_with(
        controller.model.Customer
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_customer
    assert result.customer_id == 3
    assert result.name == "Morgan Lee"
    assert result.has_account is False


def test_read_one_customer_not_found(
    db_session
):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            customer_id=999
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Customer not found"


def test_read_one_customer_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read customer"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            customer_id=1
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to read customer"
    )


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_customer_success(
    db_session,
    mocker
):
    existing_customer = mocker.Mock()
    existing_customer.customer_id = 1
    existing_customer.name = "Jamie Carter"
    existing_customer.email = "jamie@example.com"
    existing_customer.phone = "555-0100"
    existing_customer.has_account = False

    request = mocker.Mock()
    request.model_dump.return_value = {
        "phone": "555-0199",
        "has_account": True
    }

    mocker.patch(
        "api.controllers.customer.read_one",
        return_value=existing_customer
    )

    result = controller.update(
        db=db_session,
        customer_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )

    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(
        existing_customer
    )

    assert result == existing_customer
    assert result.phone == "555-0199"
    assert result.has_account is True


def test_update_customer_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.customer.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            customer_id=999,
            request=request
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Customer not found"

    db_session.commit.assert_not_called()


def test_update_customer_database_error(
    db_session,
    mocker
):
    existing_customer = mocker.Mock(
        customer_id=1,
        name="Jamie Carter",
        email="jamie@example.com",
        phone="555-0100",
        has_account=False
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "has_account": True
    }

    mocker.patch(
        "api.controllers.customer.read_one",
        return_value=existing_customer
    )

    db_session.commit.side_effect = database_error(
        "Unable to update customer"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            customer_id=1,
            request=request
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to update customer"
    )

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_customer_success(
    db_session,
    mocker
):
    existing_customer = mocker.Mock(
        customer_id=1
    )

    mocker.patch(
        "api.controllers.customer.read_one",
        return_value=existing_customer
    )

    response = controller.delete(
        db=db_session,
        customer_id=1
    )

    db_session.delete.assert_called_once_with(
        existing_customer
    )
    db_session.commit.assert_called_once()

    assert response.status_code == (
        status.HTTP_204_NO_CONTENT
    )


def test_delete_customer_not_found(
    db_session,
    mocker
):
    mocker.patch(
        "api.controllers.customer.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            customer_id=999
        )

    assert exception.value.status_code == (
        status.HTTP_404_NOT_FOUND
    )
    assert exception.value.detail == "Customer not found"

    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_customer_database_error(
    db_session,
    mocker
):
    existing_customer = mocker.Mock(
        customer_id=1
    )

    mocker.patch(
        "api.controllers.customer.read_one",
        return_value=existing_customer
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete customer"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            customer_id=1
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )
    assert exception.value.detail == (
        "Unable to delete customer"
    )

    db_session.rollback.assert_called_once()