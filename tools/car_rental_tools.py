from datetime import date, datetime
from typing import Optional, Union
from sqlalchemy import text
from langchain_core.tools import tool
from persistance.pg_db_config import get_db
from constants.sql_queries import (
    SEARCH_CAR_RENTALS_BASE,
    BOOK_CAR_RENTAL,
    UPDATE_CAR_RENTAL_CHECK,
    UPDATE_CAR_RENTAL_BASE,
    CANCEL_CAR_RENTAL
)


@tool
def search_car_rentals(
        location: Optional[str] = None,
        name: Optional[str] = None,
        price_tier: Optional[str] = None,
        start_date: Optional[Union[datetime, date]] = None,
        end_date: Optional[Union[datetime, date]] = None,
) -> list[dict]:
    """
    Search for car rentals based on location, name, price tier, start date, and end date.

    Args:
        location: The location of the car rental.
        name: The name of the car rental company.
        price_tier: The price tier of the car rental.
        start_date: The start date of the car rental.
        end_date: The end date of the car rental.

    Returns:
        A list of car rental dictionaries matching the search criteria.
    """
    db = next(get_db())
    try:
        # Base query with explicit type casting for dates
        query = text("""
            SELECT * FROM car_rentals 
            WHERE 1=1
            {location_clause}
            {name_clause}
            {price_tier_clause}
            {start_date_clause}
            {end_date_clause}
        """.format(
            location_clause="AND location ILIKE :location" if location else "",
            name_clause="AND name ILIKE :name" if name else "",
            price_tier_clause="AND price_tier = :price_tier" if price_tier else "",
            start_date_clause="AND start_date::timestamp >= :start_date" if start_date else "",
            end_date_clause="AND end_date::timestamp <= :end_date" if end_date else ""
        ))

        params = {}
        if location: params["location"] = f"%{location}%"
        if name: params["name"] = f"%{name}%"
        if price_tier: params["price_tier"] = price_tier
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date

        result = db.execute(query, params)
        rows = result.fetchall()

        if rows:
            column_names = result.keys()
            return [dict(zip(column_names, row)) for row in rows]
        return []
    finally:
        db.close()


@tool
def book_car_rental(rental_id: int) -> str:
    """
    Book a car rental by its ID.

    Args:
        rental_id: The ID of the car rental to book.

    Returns:
        A message indicating whether the car rental was successfully booked or not.
    """
    db = next(get_db())
    try:
        result = db.execute(
            text(BOOK_CAR_RENTAL),
            {"rental_id": rental_id}
        )
        db.commit()

        if result.fetchone():
            return f"Car rental {rental_id} successfully booked."
        return f"No car rental found with ID {rental_id}."
    except Exception as e:
        db.rollback()
        return f"Error booking car rental: {str(e)}"
    finally:
        db.close()


@tool
def update_car_rental(
        rental_id: int,
        start_date: Optional[Union[datetime, date]] = None,
        end_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    Update a car rental's start and end dates by its ID.

    Args:
        rental_id: The ID of the car rental to update.
        start_date: The new start date of the car rental.
        end_date: The new end date of the car rental.

    Returns:
        A message indicating whether the car rental was successfully updated or not.
    """
    db = next(get_db())
    try:
        # First check if the rental exists
        exists = db.execute(
            text(UPDATE_CAR_RENTAL_CHECK),
            {"rental_id": rental_id}
        ).fetchone()

        if not exists:
            return f"No car rental found with ID {rental_id}."

        updates = []
        params = {"rental_id": rental_id}

        if start_date:
            updates.append("start_date = :start_date")
            params["start_date"] = start_date
        if end_date:
            updates.append("end_date = :end_date")
            params["end_date"] = end_date

        if updates:
            update_query = text(
                UPDATE_CAR_RENTAL_BASE.format(updates=", ".join(updates))
            )
            result = db.execute(update_query, params)
            db.commit()

            if result.fetchone():
                return f"Car rental {rental_id} successfully updated."

        return f"No updates performed for car rental {rental_id}."
    except Exception as e:
        db.rollback()
        return f"Error updating car rental: {str(e)}"
    finally:
        db.close()


@tool
def cancel_car_rental(rental_id: int) -> str:
    """
    Cancel a car rental by its ID.

    Args:
        rental_id: The ID of the car rental to cancel.

    Returns:
        A message indicating whether the car rental was successfully cancelled or not.
    """
    db = next(get_db())
    try:
        result = db.execute(
            text(CANCEL_CAR_RENTAL),
            {"rental_id": rental_id}
        )
        db.commit()

        if result.fetchone():
            return f"Car rental {rental_id} successfully cancelled."
        return f"No car rental found with ID {rental_id}."
    except Exception as e:
        db.rollback()
        return f"Error cancelling car rental: {str(e)}"
    finally:
        db.close()
