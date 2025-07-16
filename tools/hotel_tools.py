from datetime import date, datetime
from typing import Optional, Union
from sqlalchemy import text
from persistance.pg_db_config import get_db
from langchain_core.tools import tool
from constants.sql_queries import (
    SEARCH_HOTELS_BASE,
    BOOK_HOTEL,
    UPDATE_HOTEL_CHECK,
    UPDATE_HOTEL_BASE,
    CANCEL_HOTEL
)


@tool
def search_hotels(
        location: Optional[str] = None,
        name: Optional[str] = None,
        price_tier: Optional[str] = None,
        checkin_date: Optional[Union[datetime, date]] = None,
        checkout_date: Optional[Union[datetime, date]] = None,
) -> list[dict]:
    """
    Search for hotels based on location, name, price tier, check-in date, and check-out date.

    Args:
        location: The location of the hotel.
        name: The name of the hotel.
        price_tier: The price tier of the hotel (e.g., Midscale, Upper Midscale, Upscale, Luxury).
        checkin_date: The check-in date of the hotel.
        checkout_date: The check-out date of the hotel.

    Returns:
        A list of hotel dictionaries matching the search criteria.
    """
    db = next(get_db())
    try:
        query = text(SEARCH_HOTELS_BASE)
        params = {}

        if location:
            query = text(str(query) + " AND location ILIKE :location")
            params["location"] = f"%{location}%"
        if name:
            query = text(str(query) + " AND name ILIKE :name")
            params["name"] = f"%{name}%"
        if price_tier:
            query = text(str(query) + " AND price_tier = :price_tier")
            params["price_tier"] = price_tier
        if checkin_date:
            query = text(str(query) + " AND checkin_date >= :checkin_date")
            params["checkin_date"] = checkin_date
        if checkout_date:
            query = text(str(query) + " AND checkout_date <= :checkout_date")
            params["checkout_date"] = checkout_date

        result = db.execute(query, params)
        rows = result.fetchall()

        if rows:
            column_names = result.keys()
            return [dict(zip(column_names, row)) for row in rows]
        return []
    finally:
        db.close()


@tool
def book_hotel(hotel_id: int) -> str:
    """
    Book a hotel by its ID.

    Args:
        hotel_id: The ID of the hotel to book.

    Returns:
        A message indicating whether the hotel was successfully booked or not.
    """
    db = next(get_db())
    try:
        result = db.execute(
            text(BOOK_HOTEL),
            {"hotel_id": hotel_id}
        )
        db.commit()

        if result.fetchone():
            return f"Hotel {hotel_id} successfully booked."
        return f"No hotel found with ID {hotel_id}."
    except Exception as e:
        db.rollback()
        return f"Error booking hotel: {str(e)}"
    finally:
        db.close()


@tool
def update_hotel(
        hotel_id: int,
        checkin_date: Optional[Union[datetime, date]] = None,
        checkout_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    Update a hotel's check-in and check-out dates by its ID.

    Args:
        hotel_id: The ID of the hotel to update.
        checkin_date: The new check-in date of the hotel.
        checkout_date: The new check-out date of the hotel.

    Returns:
        A message indicating whether the hotel was successfully updated or not.
    """
    db = next(get_db())
    try:
        # First check if the hotel exists
        exists = db.execute(
            text(UPDATE_HOTEL_CHECK),
            {"hotel_id": hotel_id}
        ).fetchone()

        if not exists:
            return f"No hotel found with ID {hotel_id}."

        updates = []
        params = {"hotel_id": hotel_id}

        if checkin_date:
            updates.append("checkin_date = :checkin_date")
            params["checkin_date"] = checkin_date
        if checkout_date:
            updates.append("checkout_date = :checkout_date")
            params["checkout_date"] = checkout_date

        if updates:
            update_query = text(
                UPDATE_HOTEL_BASE.format(updates=", ".join(updates))
            )
            result = db.execute(update_query, params)
            db.commit()

            if result.fetchone():
                return f"Hotel {hotel_id} successfully updated."

        return f"No updates performed for hotel {hotel_id}."
    except Exception as e:
        db.rollback()
        return f"Error updating hotel: {str(e)}"
    finally:
        db.close()


@tool
def cancel_hotel(hotel_id: int) -> str:
    """
    Cancel a hotel by its ID.

    Args:
        hotel_id: The ID of the hotel to cancel.

    Returns:
        A message indicating whether the hotel was successfully cancelled or not.
    """
    db = next(get_db())
    try:
        result = db.execute(
            text(CANCEL_HOTEL),
            {"hotel_id": hotel_id}
        )
        db.commit()

        if result.fetchone():
            return f"Hotel {hotel_id} successfully cancelled."
        return f"No hotel found with ID {hotel_id}."
    except Exception as e:
        db.rollback()
        return f"Error cancelling hotel: {str(e)}"
    finally:
        db.close()
