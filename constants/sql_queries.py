# Flight Tools
FETCH_USER_FLIGHT_INFO = """
            SELECT 
                t.ticket_no, t.book_ref,
                f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, 
                f.scheduled_departure, f.scheduled_arrival,
                bp.seat_no, tf.fare_conditions
            FROM 
                tickets t
                JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
                JOIN flights f ON tf.flight_id = f.flight_id
                JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
            WHERE 
                t.passenger_id = :passenger_id
        """

SEARCH_FLIGHTS_BASE = "SELECT * FROM flights WHERE 1=1"

UPDATE_TICKET_NEW_FLIGHT_CHECK = """
                SELECT departure_airport, arrival_airport, scheduled_departure 
                FROM flights WHERE flight_id = :flight_id
            """

FETCH_TICKET_FLIGHT_ID = """
                SELECT tf.flight_id, bp.seat_no
                FROM tickets t
                JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
                LEFT JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = tf.flight_id
                WHERE t.ticket_no = :ticket_no AND t.passenger_id = :passenger_id
            """

FETCH_TICKET_BY_PASSENGER = """
                SELECT ticket_no FROM tickets 
                WHERE ticket_no = :ticket_no AND passenger_id = :passenger_id
            """

UPDATE_TICKET_FLIGHT_ID = """
                UPDATE ticket_flights 
                SET flight_id = :flight_id 
                WHERE ticket_no = :ticket_no
            """

UPDATE_BOARDING_PASS = """
    UPDATE boarding_passes
    SET flight_id = :new_flight_id
    WHERE ticket_no = :ticket_no AND flight_id = :old_flight_id
"""

CREATE_BOARDING_PASS = """
    INSERT INTO boarding_passes (ticket_no, flight_id, seat_no, boarding_no)
    VALUES (:ticket_no, :new_flight_id, 
            'A' || (random()*100)::int::text, 
            (random()*1000)::int)
"""

DELETE_TICKET_FLIGHT = "DELETE FROM ticket_flights WHERE ticket_no = :ticket_no"

# Hotel Tools
SEARCH_HOTELS_BASE = "SELECT * FROM hotels WHERE 1=1"
BOOK_HOTEL = "UPDATE hotels SET booked = 1 WHERE id = :hotel_id RETURNING id"
UPDATE_HOTEL_CHECK = "SELECT id FROM hotels WHERE id = :hotel_id"
UPDATE_HOTEL_BASE = "UPDATE hotels SET {updates} WHERE id = :hotel_id RETURNING id"
CANCEL_HOTEL = "UPDATE hotels SET booked = FALSE WHERE id = :hotel_id RETURNING id"

# Car Rental Tools
SEARCH_CAR_RENTALS_BASE = "SELECT * FROM car_rentals WHERE 1=1"
BOOK_CAR_RENTAL = "UPDATE car_rentals SET booked = TRUE WHERE id = :rental_id RETURNING id"
UPDATE_CAR_RENTAL_CHECK = "SELECT id FROM car_rentals WHERE id = :rental_id"
UPDATE_CAR_RENTAL_BASE = "UPDATE car_rentals SET {updates} WHERE id = :rental_id RETURNING id"
CANCEL_CAR_RENTAL = "UPDATE car_rentals SET booked = FALSE WHERE id = :rental_id RETURNING id"
