from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import promo_codes as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def promo_code_request():
    return SimpleNamespace(
        promo_code="SAVE10",
        discount_amount=Decimal("10.00"),
        expiration_date=datetime(2026, 12, 31, 23, 59, 59),
        is_active=True,
        manager_id=1
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_promo_code_success(
    db_session,
    promo_code_request,
    mocker
):
    created_code = mocker.Mock()
    created_code.promo_code = "SAVE10"
    created_code.discount_amount = Decimal("10.00")
    created_code.is_active = True
    created_code.manager_id = 1

    promo_code_constructor = mocker.patch(
        "api.controllers.promo_codes.model.PromoCode",
        return_value=created_code
    )

    result = controller.create(
        db=db_session,
        request=promo_code_request
    )

    promo_code_constructor.assert_called_once_with(
        promo_code="SAVE10",
        discount_amount=Decimal("10.00"),
        expiration_date=datetime(2026, 12, 31, 23, 59, 59),
        is_active=True,
        manager_id=1
    )

    db_session.add.assert_called_once_with(created_code)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_code)

    assert result == created_code
    assert result.promo_code == "SAVE10"
    assert result.discount_amount == Decimal("10.00")
    assert result.is_active is True
    assert result.manager_id == 1


def test_create_promo_code_database_error(
    db_session,
    promo_code_request,
    mocker
):
    fake_code = mocker.Mock()

    mocker.patch(
        "api.controllers.promo_codes.model.PromoCode",
        return_value=fake_code
    )

    db_session.add.side_effect = database_error(
        "Unable to create promo code"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=promo_code_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create promo code"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_promo_codes_success(
    db_session,
    mocker
):
    code_one = mocker.Mock(promo_code="SAVE10")
    code_two = mocker.Mock(promo_code="SAVE20")
    expected_codes = [code_one, code_two]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_codes

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.PromoCode
    )
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_codes
    assert len(result) == 2


def test_read_all_promo_codes_empty(
    db_session
):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_promo_codes_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read promo codes"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read promo codes"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_promo_code_success(
    db_session,
    mocker
):
    expected_code = mocker.Mock()
    expected_code.promo_code = "SAVE10"
    expected_code.discount_amount = Decimal("10.00")
    expected_code.is_active = True

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_code

    result = controller.read_one(
        db=db_session,
        promo_code="SAVE10"
    )

    db_session.query.assert_called_once_with(
        controller.model.PromoCode
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_code
    assert result.promo_code == "SAVE10"
    assert result.discount_amount == Decimal("10.00")
    assert result.is_active is True


def test_read_one_promo_code_not_found(
    db_session
):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            promo_code="MISSING"
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Promo code not found"


def test_read_one_promo_code_database_error(
    db_session
):
    db_session.query.side_effect = database_error(
        "Unable to read promo code"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            promo_code="SAVE10"
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read promo code"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_promo_code_success(
    db_session,
    mocker
):
    existing_code = mocker.Mock()
    existing_code.promo_code = "SAVE10"
    existing_code.discount_amount = Decimal("10.00")
    existing_code.is_active = True
    existing_code.manager_id = 1

    request = mocker.Mock()
    request.model_dump.return_value = {
        "discount_amount": Decimal("15.00"),
        "is_active": False
    }

    mocker.patch(
        "api.controllers.promo_codes.read_one",
        return_value=existing_code
    )

    result = controller.update(
        db=db_session,
        promo_code="SAVE10",
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_code)

    assert result == existing_code
    assert result.discount_amount == Decimal("15.00")
    assert result.is_active is False


def test_update_promo_code_not_found(
    db_session,
    mocker
):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.promo_codes.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            promo_code="MISSING",
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Promo code not found"
    db_session.commit.assert_not_called()


def test_update_promo_code_database_error(
    db_session,
    mocker
):
    existing_code = mocker.Mock(
        promo_code="SAVE10",
        discount_amount=Decimal("10.00"),
        is_active=True
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "discount_amount": Decimal("20.00")
    }

    mocker.patch(
        "api.controllers.promo_codes.read_one",
        return_value=existing_code
    )

    db_session.commit.side_effect = database_error(
        "Unable to update promo code"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            promo_code="SAVE10",
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update promo code"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_promo_code_success(
    db_session,
    mocker
):
    existing_code = mocker.Mock(promo_code="SAVE10")

    mocker.patch(
        "api.controllers.promo_codes.read_one",
        return_value=existing_code
    )

    response = controller.delete(
        db=db_session,
        promo_code="SAVE10"
    )

    db_session.delete.assert_called_once_with(existing_code)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_promo_code_not_found(
    db_session,
    mocker
):
    mocker.patch(
        "api.controllers.promo_codes.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promo code not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            promo_code="MISSING"
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Promo code not found"
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_promo_code_database_error(
    db_session,
    mocker
):
    existing_code = mocker.Mock(promo_code="SAVE10")

    mocker.patch(
        "api.controllers.promo_codes.read_one",
        return_value=existing_code
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete promo code"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            promo_code="SAVE10"
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete promo code"
    db_session.rollback.assert_called_once()