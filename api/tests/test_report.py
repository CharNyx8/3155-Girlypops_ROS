from types import SimpleNamespace
from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..controllers import report as controller


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def report_request():
    return SimpleNamespace(
        report_name="Daily Revenue Report",
        generated_by_manager_id=1
    )


def database_error(message):
    error = SQLAlchemyError(message)
    error.__dict__["orig"] = message
    return error


# ---------------------------------------------------------
# FIND MANAGER
# ---------------------------------------------------------

def test_find_manager_success(db_session, mocker):
    expected_manager = mocker.Mock(manager_id=1)

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_manager

    result = controller.find_manager(
        db=db_session,
        manager_id=1
    )

    db_session.query.assert_called_once_with(
        controller.manager_model.RestaurantManager
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_manager
    assert result.manager_id == 1


def test_find_manager_not_found(db_session):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.find_manager(
            db=db_session,
            manager_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Restaurant manager not found"


# ---------------------------------------------------------
# DAILY REVENUE
# ---------------------------------------------------------
def test_read_daily_revenue_success(db_session):
    query = db_session.query.return_value
    joined_query = query.join.return_value
    filtered_query = joined_query.filter.return_value
    filtered_query.first.return_value = (
        3,
        Decimal("75.50")
    )

    result = controller.read_daily_revenue(
        db=db_session,
        report_date=date(2026, 7, 31)
    )

    assert result == {
        "report_date": date(2026, 7, 31),
        "order_count": 3,
        "total_revenue": Decimal("75.50")
    }


def test_read_daily_revenue_no_sales(db_session):
    query = db_session.query.return_value
    joined_query = query.join.return_value
    filtered_query = joined_query.filter.return_value
    filtered_query.first.return_value = (
        0,
        Decimal("0.00")
    )

    result = controller.read_daily_revenue(
        db=db_session,
        report_date=date(2026, 7, 31)
    )

    assert result["order_count"] == 0
    assert result["total_revenue"] == Decimal("0.00")


# ---------------------------------------------------------
# MENU PERFORMANCE
# ---------------------------------------------------------
def test_read_menu_performance_success(db_session, mocker):
    row_one = mocker.Mock(
        item_id=2,
        item_name="Garden Salad",
        quantity_sold=0
    )
    row_two = mocker.Mock(
        item_id=1,
        item_name="Classic Burger",
        quantity_sold=5
    )

    query = db_session.query.return_value
    joined_query = query.outerjoin.return_value
    grouped_query = joined_query.group_by.return_value
    ordered_query = grouped_query.order_by.return_value
    ordered_query.all.return_value = [
        row_one,
        row_two
    ]

    result = controller.read_menu_performance(
        db=db_session
    )

    assert result == [
        {
            "item_id": 2,
            "item_name": "Garden Salad",
            "quantity_sold": 0
        },
        {
            "item_id": 1,
            "item_name": "Classic Burger",
            "quantity_sold": 5
        }
    ]


def test_read_menu_performance_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to calculate menu performance"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_menu_performance(
            db=db_session
        )

    assert exception.value.status_code == (
        status.HTTP_400_BAD_REQUEST
    )


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

def test_create_report_success(
    db_session,
    report_request,
    mocker
):
    created_report = mocker.Mock()
    created_report.report_id = 1
    created_report.report_name = "Daily Revenue Report"
    created_report.generated_by_manager_id = 1

    mocker.patch(
        "api.controllers.report.find_manager",
        return_value=mocker.Mock(manager_id=1)
    )

    report_constructor = mocker.patch(
        "api.controllers.report.model.Report",
        return_value=created_report
    )

    result = controller.create(
        db=db_session,
        request=report_request
    )

    report_constructor.assert_called_once_with(
        report_name="Daily Revenue Report",
        generated_by_manager_id=1
    )

    db_session.add.assert_called_once_with(created_report)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_report)

    assert result == created_report
    assert result.report_id == 1
    assert result.report_name == "Daily Revenue Report"


def test_create_report_without_manager_success(
    db_session,
    mocker
):
    request = SimpleNamespace(
        report_name="Unassigned Report",
        generated_by_manager_id=None
    )

    created_report = mocker.Mock(
        report_id=2,
        report_name="Unassigned Report",
        generated_by_manager_id=None
    )

    find_manager = mocker.patch(
        "api.controllers.report.find_manager"
    )

    mocker.patch(
        "api.controllers.report.model.Report",
        return_value=created_report
    )

    result = controller.create(
        db=db_session,
        request=request
    )

    find_manager.assert_not_called()
    db_session.add.assert_called_once_with(created_report)
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_report)

    assert result == created_report
    assert result.generated_by_manager_id is None


def test_create_report_manager_not_found(
    db_session,
    report_request,
    mocker
):
    mocker.patch(
        "api.controllers.report.find_manager",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant manager not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=report_request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Restaurant manager not found"

    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()


def test_create_report_database_error(
    db_session,
    report_request,
    mocker
):
    fake_report = mocker.Mock()

    mocker.patch(
        "api.controllers.report.find_manager",
        return_value=mocker.Mock(manager_id=1)
    )

    mocker.patch(
        "api.controllers.report.model.Report",
        return_value=fake_report
    )

    db_session.add.side_effect = database_error(
        "Unable to create report"
    )

    with pytest.raises(HTTPException) as exception:
        controller.create(
            db=db_session,
            request=report_request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to create report"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# READ ALL
# ---------------------------------------------------------

def test_read_all_reports_success(db_session, mocker):
    report_one = mocker.Mock(report_id=1)
    report_two = mocker.Mock(report_id=2)
    expected_reports = [report_one, report_two]

    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = expected_reports

    result = controller.read_all(db=db_session)

    db_session.query.assert_called_once_with(
        controller.model.Report
    )
    query.order_by.assert_called_once()
    ordered_query.all.assert_called_once()

    assert result == expected_reports
    assert len(result) == 2


def test_read_all_reports_empty(db_session):
    query = db_session.query.return_value
    ordered_query = query.order_by.return_value
    ordered_query.all.return_value = []

    result = controller.read_all(db=db_session)

    assert result == []


def test_read_all_reports_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read reports"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_all(db=db_session)

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read reports"


# ---------------------------------------------------------
# READ ONE
# ---------------------------------------------------------

def test_read_one_report_success(db_session, mocker):
    expected_report = mocker.Mock()
    expected_report.report_id = 3
    expected_report.report_name = "Weekly Sales Report"

    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = expected_report

    result = controller.read_one(
        db=db_session,
        report_id=3
    )

    db_session.query.assert_called_once_with(
        controller.model.Report
    )
    query.filter.assert_called_once()
    filtered_query.first.assert_called_once()

    assert result == expected_report
    assert result.report_id == 3
    assert result.report_name == "Weekly Sales Report"


def test_read_one_report_not_found(db_session):
    query = db_session.query.return_value
    filtered_query = query.filter.return_value
    filtered_query.first.return_value = None

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            report_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Report not found"


def test_read_one_report_database_error(db_session):
    db_session.query.side_effect = database_error(
        "Unable to read report"
    )

    with pytest.raises(HTTPException) as exception:
        controller.read_one(
            db=db_session,
            report_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to read report"


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

def test_update_report_success(db_session, mocker):
    existing_report = mocker.Mock()
    existing_report.report_id = 1
    existing_report.report_name = "Old Report"
    existing_report.generated_by_manager_id = 1

    request = mocker.Mock()
    request.model_dump.return_value = {
        "report_name": "Updated Report"
    }

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    find_manager = mocker.patch(
        "api.controllers.report.find_manager"
    )

    result = controller.update(
        db=db_session,
        report_id=1,
        request=request
    )

    request.model_dump.assert_called_once_with(
        exclude_unset=True
    )
    find_manager.assert_not_called()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_report)

    assert result == existing_report
    assert result.report_name == "Updated Report"


def test_update_report_manager_success(db_session, mocker):
    existing_report = mocker.Mock(
        report_id=1,
        report_name="Daily Report",
        generated_by_manager_id=1
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "generated_by_manager_id": 2
    }

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    find_manager = mocker.patch(
        "api.controllers.report.find_manager",
        return_value=mocker.Mock(manager_id=2)
    )

    result = controller.update(
        db=db_session,
        report_id=1,
        request=request
    )

    find_manager.assert_called_once_with(
        db=db_session,
        manager_id=2
    )
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(existing_report)

    assert result == existing_report
    assert result.generated_by_manager_id == 2


def test_update_report_manager_to_none(
    db_session,
    mocker
):
    existing_report = mocker.Mock(
        report_id=1,
        generated_by_manager_id=1
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "generated_by_manager_id": None
    }

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    find_manager = mocker.patch(
        "api.controllers.report.find_manager"
    )

    result = controller.update(
        db=db_session,
        report_id=1,
        request=request
    )

    find_manager.assert_not_called()
    db_session.commit.assert_called_once()
    assert result.generated_by_manager_id is None


def test_update_report_not_found(db_session, mocker):
    request = mocker.Mock()

    mocker.patch(
        "api.controllers.report.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            report_id=999,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Report not found"
    db_session.commit.assert_not_called()


def test_update_report_manager_not_found(
    db_session,
    mocker
):
    existing_report = mocker.Mock(
        report_id=1,
        generated_by_manager_id=1
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "generated_by_manager_id": 999
    }

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    mocker.patch(
        "api.controllers.report.find_manager",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant manager not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            report_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Restaurant manager not found"
    db_session.commit.assert_not_called()


def test_update_report_database_error(db_session, mocker):
    existing_report = mocker.Mock(
        report_id=1,
        report_name="Daily Report"
    )

    request = mocker.Mock()
    request.model_dump.return_value = {
        "report_name": "Updated Report"
    }

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    db_session.commit.side_effect = database_error(
        "Unable to update report"
    )

    with pytest.raises(HTTPException) as exception:
        controller.update(
            db=db_session,
            report_id=1,
            request=request
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to update report"
    db_session.rollback.assert_called_once()


# ---------------------------------------------------------
# DELETE
# ---------------------------------------------------------

def test_delete_report_success(db_session, mocker):
    existing_report = mocker.Mock(report_id=1)

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    response = controller.delete(
        db=db_session,
        report_id=1
    )

    db_session.delete.assert_called_once_with(existing_report)
    db_session.commit.assert_called_once()

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_report_not_found(db_session, mocker):
    mocker.patch(
        "api.controllers.report.read_one",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            report_id=999
        )

    assert exception.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception.value.detail == "Report not found"
    db_session.delete.assert_not_called()
    db_session.commit.assert_not_called()


def test_delete_report_database_error(db_session, mocker):
    existing_report = mocker.Mock(report_id=1)

    mocker.patch(
        "api.controllers.report.read_one",
        return_value=existing_report
    )

    db_session.delete.side_effect = database_error(
        "Unable to delete report"
    )

    with pytest.raises(HTTPException) as exception:
        controller.delete(
            db=db_session,
            report_id=1
        )

    assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.value.detail == "Unable to delete report"
    db_session.rollback.assert_called_once()