from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import reviews as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def review_request():
    return SimpleNamespace(
        rating=5,
        comment="Excellent food",
        customer_id=1,
        item_id=2
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_review_success(
    db_session,
    review_request,
    mocker
):
    customer = mocker.Mock(customer_id=1)
    menu_item = mocker.Mock(item_id=2)

    customer_query = mocker.Mock()
    customer_query.filter.return_value.first.return_value = customer

    menu_item_query = mocker.Mock()
    menu_item_query.filter.return_value.first.return_value = menu_item

    db_session.query.side_effect = [
        customer_query,
        menu_item_query
    ]

    created_review = mocker.Mock()
    created_review.review_id = 1
    created_review.rating = 5

    review_constructor = mocker.patch(
        "api.controllers.reviews.model.Review",
        return_value=created_review
    )

    result = controller.create(
        db=db_session,
        request=review_request
    )

    review_constructor.assert_called_once_with(
        rating=5,
        comment="Excellent food",
        customer_id=1,
        item_id=2
    )

    db_session.add.assert_called_once_with(created_review)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_review)

    assert result == created_review
    assert result.review_id == 1
    assert result.rating == 5


def test_create_review_customer_not_found(
    db_session,
    review_request,
    mocker
):
    customer_query = mocker.Mock()
    customer_query.filter.return_value.first.return_value = None
    db_session.query.return_value = customer_query

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=review_request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Customer not found"

    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


def test_create_review_menu_item_not_found(
    db_session,
    review_request,
    mocker
):
    customer = mocker.Mock(customer_id=1)

    customer_query = mocker.Mock()
    customer_query.filter.return_value.first.return_value = customer

    menu_item_query = mocker.Mock()
    menu_item_query.filter.return_value.first.return_value = None

    db_session.query.side_effect = [
        customer_query,
        menu_item_query
    ]

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=review_request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Menu item not found"

    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


def test_create_review_database_error(
    db_session,
    review_request,
    mocker
):
    customer_query = mocker.Mock()
    customer_query.filter.return_value.first.return_value = mocker.Mock()

    menu_item_query = mocker.Mock()
    menu_item_query.filter.return_value.first.return_value = mocker.Mock()

    db_session.query.side_effect = [
        customer_query,
        menu_item_query
    ]

    fake_review = mocker.Mock()

    mocker.patch(
        "api.controllers.reviews.model.Review",
        return_value=fake_review
    )

    db_session.add.side_effect = database_error(
        "Unable to create review"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=review_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create review"

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_reviews_success(db_session, mocker):
    review_one = mocker.Mock(review_id=1)
    review_two = mocker.Mock(review_id=2)
    expected_reviews = [review_one, review_two]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_reviews

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(controller.model.Review)
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_reviews
    assert len(result) == 2


def test_read_all_reviews_empty(db_session):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_reviews_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read reviews"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read reviews"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_review_success(db_session, mocker):
    expected_review = mocker.Mock()
    expected_review.review_id = 3
    expected_review.rating = 4

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_review

    result = controller.read_one(
        db=db_session,
        review_id=3
    )

    db_session.query.assert_called_once_with(controller.model.Review)
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_review
    assert result.review_id == 3
    assert result.rating == 4


def test_read_one_review_not_found(db_session):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            review_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Review not found"


def test_read_one_review_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read review"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            review_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read review"


# ---------------------------------------------------------
# READ BY MENU ITEM
# ---------------------------------------------------------

def test_read_reviews_by_menu_item_success(
    db_session,
    mocker
):
    menu_item_query = mocker.Mock()
    menu_item_query.filter.return_value.first.return_value = mocker.Mock(
        item_id=2
    )

    review_one = mocker.Mock(review_id=1, item_id=2)
    review_two = mocker.Mock(review_id=2, item_id=2)
    expected_reviews = [review_one, review_two]

    reviews_query = mocker.Mock()
    filtered_reviews = reviews_query.filter.return_value
    ordered_reviews = filtered_reviews.order_by.return_value
    ordered_reviews.all.return_value = expected_reviews

    db_session.query.side_effect = [
        menu_item_query,
        reviews_query
    ]

    result = controller.read_by_menu_item(
        db=db_session,
        item_id=2
    )

    assert result == expected_reviews
    assert len(result) == 2


def test_read_reviews_by_menu_item_not_found(
    db_session,
    mocker
):
    menu_item_query = mocker.Mock()
    menu_item_query.filter.return_value.first.return_value = None
    db_session.query.return_value = menu_item_query

    with pytest.raises(HTTPException) as exception:
        controller.read_by_menu_item(
            db=db_session,
            item_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Menu item not found"


def test_read_reviews_by_menu_item_database_error(
    db_session,
    mocker
):
    menu_item_query = mocker.Mock()
    menu_item_query.filter.return_value.first.return_value = mocker.Mock(
        item_id=2
    )

    db_session.query.side_effect = [
        menu_item_query,
        database_error("Unable to read menu item reviews")
    ]

    with pytest.raises(HTTPException) as exception:
        controller.read_by_menu_item(
            db=db_session,
            item_id=2
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read menu item reviews"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_review_success(db_session, mocker):
    existing_review = mocker.Mock()
    existing_review.review_id = 1
    existing_review.rating = 3
    existing_review.comment = "Original comment"

    request = mocker.Mock()
    request.model_dump.return_value = {
        "rating": 5,
        "comment": "Updated review"
    }

    mocker.patch(
        "api.controllers.reviews.read_one",
        return_value=existing_review
    )

    result = controller.update(
        db=db_session,
        review_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(exclude_unset=True)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_review)

    assert result == existing_review
    assert result.rating == 5
    assert result.comment == "Updated review"


def test_update_review_not_found(db_session, mocker):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.reviews.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            review_id=999,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Review not found"

    db_session.commit.assert_not_called()


def test_update_review_database_error(db_session, mocker):
    existing_review = mocker.Mock(review_id=1)

    request = mocker.Mock()
    request.model_dump.return_value = {
        "rating": 2
    }

    mocker.patch(
        "api.controllers.reviews.read_one",
        return_value=existing_review
    )

    db_session.commit.side_effect = database_error(
        "Unable to update review"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            review_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update review"

    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_review_success(db_session, mocker):
    existing_review = mocker.Mock(review_id=1)

    mocker.patch(
        "api.controllers.reviews.read_one",
        return_value=existing_review
    )

    response = controller.delete(
        db=db_session,
        review_id=1
    )

    db_session.delete.assert_called_once_with(existing_review)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_review_not_found(db_session, mocker):
    mocker.patch(
        "api.controllers.reviews.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            review_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Review not found"

    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_review_database_error(db_session, mocker):
    existing_review = mocker.Mock(review_id=1)

    mocker.patch(
        "api.controllers.reviews.read_one",
        return_value=existing_review
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete review"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            review_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete review"

    db_session.rollback.assert_called_once()