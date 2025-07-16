from datetime import date, datetime
from typing import Optional, Union
import pytz
from sqlalchemy import text
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from persistance.pg_db_config import get_db
from constants.sql_queries import (
    FETCH_USER_FLIGHT_INFO,
    SEARCH_FLIGHTS_BASE,
    UPDATE_TICKET_NEW_FLIGHT_CHECK,
    FETCH_TICKET_FLIGHT_ID,
    FETCH_TICKET_BY_PASSENGER,
    UPDATE_TICKET_FLIGHT_ID,
    DELETE_TICKET_FLIGHT, UPDATE_BOARDING_PASS, CREATE_BOARDING_PASS
)


@tool
def fetch_user_flight_information(config: RunnableConfig) -> list[dict]:
    """Fetch all tickets for the user along with corresponding flight information and seat assignments."""
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id")
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    db = next(get_db())
    try:
        query = text(FETCH_USER_FLIGHT_INFO)

        result = db.execute(query, {"passenger_id": passenger_id})
        rows = result.fetchall()

        if rows:
            column_names = result.keys()
            return [dict(zip(column_names, row)) for row in rows]
        return []
    finally:
        db.close()


@tool
def search_flights(
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        start_time: Optional[Union[datetime, date]] = None,
        end_time: Optional[Union[datetime, date]] = None,
        limit: int = 20,
) -> list[dict]:
    """Search for flights based on departure airport, arrival airport, and departure time range."""
    db = next(get_db())
    try:
        base_query = SEARCH_FLIGHTS_BASE
        params = {}

        if departure_airport:
            base_query += " AND departure_airport = :departure_airport"
            params["departure_airport"] = departure_airport
        if arrival_airport:
            base_query += " AND arrival_airport = :arrival_airport"
            params["arrival_airport"] = arrival_airport
        if start_time:
            base_query += " AND scheduled_departure >= :start_time"
            params["start_time"] = start_time
        if end_time:
            base_query += " AND scheduled_departure <= :end_time"
            params["end_time"] = end_time

        base_query += " LIMIT :limit"
        params["limit"] = limit

        result = db.execute(text(base_query), params)
        rows = result.fetchall()

        if rows:
            column_names = result.keys()
            return [dict(zip(column_names, row)) for row in rows]
        return []
    finally:
        db.close()


@tool
def update_ticket_to_new_flight(
        ticket_no: str,
        new_flight_id: int,
        *,
        config: RunnableConfig
) -> str:
    """Update the user's ticket to a new valid flight."""
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id")
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    db = next(get_db())
    try:
        # Check new flight exists
        new_flight = db.execute(
            text(UPDATE_TICKET_NEW_FLIGHT_CHECK),
            {"flight_id": new_flight_id}
        ).fetchone()

        if not new_flight:
            return "Invalid new flight ID provided."

        # Convert to dict
        column_names = ['departure_airport', 'arrival_airport', 'scheduled_departure']
        new_flight_dict = dict(zip(column_names, new_flight))

        # Check time restriction
        timezone = pytz.timezone("Etc/GMT-3")
        current_time = datetime.now(tz=timezone)
        departure_time = new_flight_dict["scheduled_departure"]

        if isinstance(departure_time, str):
            departure_time = datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S.%f%z")

        time_until = (departure_time - current_time).total_seconds()
        if time_until < (3 * 3600):
            return f"Not permitted to reschedule to a flight that is less than 3 hours from the current time. Selected flight is at {departure_time}."

        # Check current ticket exists
        current_flight = db.execute(
            text(FETCH_TICKET_FLIGHT_ID),
            {"ticket_no": ticket_no, "passenger_id": passenger_id}
        ).fetchone()

        if not current_flight:
            return "No existing ticket found for the given ticket number."

        old_flight_id, seat_no = current_flight

        # Verify ticket ownership
        current_ticket = db.execute(
            text(FETCH_TICKET_BY_PASSENGER),
            {"ticket_no": ticket_no, "passenger_id": passenger_id}
        ).fetchone()

        if not current_ticket:
            return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

        # Update the ticket
        db.execute(
            text(UPDATE_TICKET_FLIGHT_ID),
            {"flight_id": new_flight_id, "ticket_no": ticket_no}
        )

        if seat_no:
            db.execute(
                text(UPDATE_BOARDING_PASS),
                {
                    "new_flight_id": new_flight_id,
                    "ticket_no": ticket_no,
                    "old_flight_id": old_flight_id
                }
            )
        else:
            db.execute(
                text(CREATE_BOARDING_PASS),
                {"ticket_no": ticket_no, "new_flight_id": new_flight_id}
            )

        db.commit()
        return "Ticket successfully updated to new flight."
    except Exception as e:
        db.rollback()
        return f"Error updating ticket: {str(e)}"
    finally:
        db.close()


@tool
def cancel_ticket(ticket_no: str, *, config: RunnableConfig) -> str:
    """Cancel the user's ticket and remove it from the database."""
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id")
    if not passenger_id:
        raise ValueError("No passenger ID configured.")

    db = next(get_db())
    try:
        # Check ticket exists
        existing_ticket = db.execute(
            text(FETCH_TICKET_FLIGHT_ID),
            {"ticket_no": ticket_no}
        ).fetchone()

        if not existing_ticket:
            return "No existing ticket found for the given ticket number."

        # Verify ticket ownership
        current_ticket = db.execute(
            text(FETCH_TICKET_BY_PASSENGER),
            {"ticket_no": ticket_no, "passenger_id": passenger_id}
        ).fetchone()

        if not current_ticket:
            return f"Current signed-in passenger with ID {passenger_id} not the owner of ticket {ticket_no}"

        # Delete the ticket
        db.execute(
            text(DELETE_TICKET_FLIGHT),
            {"ticket_no": ticket_no}
        )
        db.commit()
        return "Ticket successfully canceled."
    except Exception as e:
        db.rollback()
        return f"Error canceling ticket: {str(e)}"
    finally:
        db.close()
