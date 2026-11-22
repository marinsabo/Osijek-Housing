from app.core.errors import InvalidInput
from app.core.models import Landlord, Neighbourhood, Flat

def create_flat(session, landlord_id, area_m2, number_of_rooms, street, house_number,
                parking_type, neighbourhood_id, longitude, latitude, floor = None, unit = None):
    """Validate a new flat and save it to the database.

    Args:
        session: An open database session. The caller opens and closes it.
        landlord_id: user_id of an existing landlord.
        area_m2: Floor area in square metres, greater than 0.
        number_of_rooms: Whole number, greater than 0.
        street: Street name, not empty.
        house_number: House number as text, e.g. "4a".
        parking_type: Type of parking, not empty.
        neighbourhood_id: id of an existing neighbourhood.
        longitude: Map pin longitude in GPS degrees (about 18.7 in Osijek).
        latitude: Map pin latitude in GPS degrees (about 45.5 in Osijek).
        floor: Floor number, or None for a house.
        unit: Flat or unit number, or None.

    Returns:
        The saved Flat, with its id filled in.

    Raises:
        InvalidInput: If a value is missing or invalid. Its field is the
            name of the wrong argument, its message can be shown to the user.
    """

    # Validate everything before touching the database. If any check fails, nothing is saved.
    # session.get(Model, id) looks up one row by its primary key and returns None if there is none.
    if session.get(Landlord, landlord_id) is None:
        raise InvalidInput("landlord_id", "Landlord is not specified or does not exist in database.")
    if area_m2 is None:
        raise InvalidInput("area_m2", "Flat area is not specified.")
    if area_m2 <= 0:
        raise InvalidInput("area_m2", "Flat area must be greater than 0.")
    if number_of_rooms is None:
        raise InvalidInput("number_of_rooms", "Number of rooms is not specified.")
    if number_of_rooms <= 0:
        raise InvalidInput("number_of_rooms", "Number of rooms must be greater than 0.")
    # "not x" catches both None and empty text; strip() catches text made only of spaces.
    if not street or len(street.strip()) == 0:
        raise InvalidInput("street", "Street is not specified.")
    if not house_number or len(house_number.strip()) == 0:
        raise InvalidInput("house_number", "House number is not specified.")
    if not parking_type or len(parking_type.strip()) == 0:
        raise InvalidInput("parking_type", "Parking type is not specified.")
    if session.get(Neighbourhood, neighbourhood_id) is None:
        raise InvalidInput("neighbourhood_id", "Neighbourhood is not specified or does not exist in database.")
    if longitude is None:
        raise InvalidInput("longitude", "Longitude is not specified.")
    if latitude is None:
        raise InvalidInput("latitude", "Latitude is not specified.")

    # PostGIS reads a point as EWKT text: SRID=4326 means GPS coordinates, longitude comes before latitude,
    # separated by a space. At commit, GeoAlchemy2 wraps this text in ST_GeogFromText,
    # and PostGIS stores it as a binary geography point.
    location = f"SRID=4326;POINT({longitude} {latitude})"

    # A Flat object in Python memory only; nothing is in the database yet. 
    # id and archived_at are left out: Postgres fills id from its counter at commit, and archived_at stays empty.
    flat = Flat(landlord_id = landlord_id, area_m2 = area_m2, number_of_rooms = number_of_rooms, street = street, 
                house_number = house_number, floor = floor, unit = unit, parking_type = parking_type,
                neighbourhood_id = neighbourhood_id, location = location)

    # Stage the flat in the session (like putting it in a cart). Still not sent to the database.
    session.add(flat)

    # Send everything staged to the database in one transaction and make it permanent. 
    # Postgres fills in id and runs its own checks (area_m2 > 0, foreign keys) here.
    session.commit()

    # Reload the row from the database, so flat has its real id and stored values.
    session.refresh(flat)

    # Return the saved flat, so the caller can use its id, e.g. to create a listing for it.
    return flat
    
