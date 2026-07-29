from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import payments as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def payment_request():
    return SimpleNamespace(
        order_id=1,
        payment_method="Card",
        payment_status="Paid",
        amount=Decimal("24.99")
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_payment_success(
    db_session,
    payment_request,
    mocker
):
    created_payment = mocker.Mock()
    created_payment.payment_id = 1
    created_payment.order_id = 1
    created_payment.payment_method = "Card"
    created_payment.payment_status = "Paid"
    created_payment.amount = Decimal("24.99")

    payment_constructor = mocker.patch(
        "api.controllers.payments.model.Payment",
        return_value=created_payment
    )

    result = controller.create(
        db=db_session,
        request=payment_request
    )

    payment_constructor.assert_called_once_with(
        order_id=1,
        payment_method="Card",
        payment_status="Paid",
        amount=Decimal("24.99")
    )

    db_session.add.assert_called_once_with(created_payment)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_payment)

    assert result == created_payment
    assert result.payment_id == 1
    assert result.order_id == 1
    assert result.payment_status == "Paid"


def test_create_payment_database_error(
    db_session,
    payment_request,
    mocker
):
    fake_payment = mocker.Mock()

    mocker.patch(
        "api.controllers.payments.model.Payment",
        return_value=fake_payment
    )

    db_session.add.side_effect = database_error(
        "Unable to create payment"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=payment_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create payment"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_payments_success(
    db_session,
    mocker
):
    payment_one = mocker.Mock(payment_id=1)
    payment_two = mocker.Mock(payment_id=2)

    expected_payments = [
        payment_one,
        payment_two
    ]

    query = db_session.query.return_value
    query.all.return_value = expected_payments

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.Payment
    )
    query.all.assert_called_once()

    assert result == expected_payments
    assert len(result) == 2


def test_read_all_payments_empty(
    db_session
):
    query = db_session.query.return_value
    query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_payments_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read payments"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read payments"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_payment_success(
    db_session,
    mocker
):
    expected_payment = mocker.Mock()
    expected_payment.payment_id = 3
    expected_payment.order_id = 4
    expected_payment.payment_status = "Pending"

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_payment

    result = controller.read_one(
        db=db_session,
        payment_id=3
    )

    db_session.query.assert_called_once_with(
        controller.model.Payment
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_payment
    assert result.payment_id == 3
    assert result.order_id == 4
    assert result.payment_status == "Pending"


def test_read_one_payment_not_found(
    db_session
):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            payment_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Payment not found"


def test_read_one_payment_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read payment"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            payment_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read payment"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_payment_success(
    db_session,
    mocker
):
    existing_payment = mocker.Mock()
    existing_payment.payment_id = 1
    existing_payment.order_id = 1
    existing_payment.payment_method = "Card"
    existing_payment.payment_status = "Pending"
    existing_payment.amount = Decimal("24.99")

    request = mocker.Mock()
    request.model_dump.return_value = {
        "payment_status": "Paid",
        "amount": Decimal("29.99")
    }

    mocker.patch(
        "api.controllers.payments.read_one",
        return_value=existing_payment
    )

    result = controller.update(
        db=db_session,
        payment_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )

    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(
        existing_payment
    )

    assert result == existing_payment
    assert result.payment_status == "Paid"
    assert result.amount == Decimal("29.99")


def test_update_payment_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.payments.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            payment_id=999,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Payment not found"
    db_session.commit.assert_not_called()


def test_update_payment_database_error(
    db_session,
    mocker
):
    existing_payment = mocker.Mock(
        payment_id=1,
        payment_status="Pending"
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "payment_status": "Paid"
    }

    mocker.patch(
        "api.controllers.payments.read_one",
        return_value=existing_payment
    )

    db_session.commit.side_effect = database_error(
        "Unable to update payment"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            payment_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update payment"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_payment_success(
    db_session,
    mocker
):
    existing_payment = mocker.Mock(payment_id=1)

    mocker.patch(
        "api.controllers.payments.read_one",
        return_value=existing_payment
    )

    response = controller.delete(
        db=db_session,
        payment_id=1
    )

    db_session.delete.assert_called_once_with(existing_payment)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_payment_not_found(
    db_session,
    mocker
):
    mocker.patch(
        "api.controllers.payments.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            payment_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Payment not found"
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_payment_database_error(
    db_session,
    mocker
):
    existing_payment = mocker.Mock(payment_id=1)

    mocker.patch(
        "api.controllers.payments.read_one",
        return_value=existing_payment
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete payment"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            payment_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete payment"
    db_session.rollback.assert_called_once()