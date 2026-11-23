from app.core.errors import InvalidInput
from app.core.models import Landlord, Neighbourhood, Flat, Listing
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import select

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
    
def create_listing(session, flat_id, price, description, utilities_included):
    """Validate a new listing and save it to the database.

    Args:
        session: An open database session. The caller opens and closes it.
        flat_id: id of an existing flat.
        price: price of the listing in euros, greater than 0.
        description: description of the listing, cannot be empty.
        utilities_included: indicates if utilities are included in the price, True or False (bool).

    Returns:
        The saved Listing, with its id, published_at and updated_at filled in.

    Raises:
        InvalidInput: If a value is missing or invalid. Its field is the
            name of the wrong argument, its message can be shown to the user.
    """

    flat = session.get(Flat, flat_id)

    if flat is None:
        raise InvalidInput("flat_id", "Flat is not specified or does not exist in database.")
    # Checks if the flat for which listing is being made is archived. In order to be published,
    # flat mustn't be archived.
    if flat.archived_at is not None:
        raise InvalidInput("flat_id", "Flat cannot be archived in order to publish listing.")
    if price is None:
        raise InvalidInput("price", "Price is not specified.")
    if price <= 0:
        raise InvalidInput("price", "Price must be greater than 0.")
    if not description or len(description.strip()) == 0:
        raise InvalidInput("description", "Description is not specified.")
    if len(description) > 1000:
        raise InvalidInput("description", "Description can be maximum of 1000 characters long.")
    if not isinstance(utilities_included, bool):
        raise InvalidInput("utilities_included", "Utilities are not specified or the value is wrong.")

    listing = Listing(flat_id = flat_id, price = price, description = description,
                        utilities_included = utilities_included)
    
    session.add(listing)
    session.commit()
    session.refresh(listing)

    return listing

def get_listing(session, listing_id):
    """Return the listing if it exists in database. Returns None if it doesn't.

    Args:
        session: An open database session. The caller opens and closes it.
        listing_id: id of a listing that is requested.

    Returns:
        Listing object with its flat loaded, or None if there is no listing with that id.
    """
    # Loads both listing and its matching flat (flat: Mapped["Flat"] = relationship() field).
    listing = session.get(Listing, listing_id, options=[joinedload(Listing.flat)])

    return listing

def list_listings(session, min_price=None, max_price=None, rooms=None):
    """Return open listings that match the filters, newest first.

    A listing is open if it is not taken, not archived and its flat is not archived.
    A filter left as None is not applied.

    Args:
        session: An open database session. The caller opens and closes it.
        min_price: Lowest price in euros, inclusive, 0 or more.
        max_price: Highest price in euros, inclusive, 0 or more, not lower than min_price.
        rooms: Exact number of rooms of the flat, greater than 0.

    Returns:
        List of Listing objects with their flat loaded. Empty list if nothing matches.

    Raises:
        InvalidInput: If a filter is invalid. Its field is the
            name of the wrong argument, its message can be shown to the user.
    """
    if min_price is not None and min_price < 0:
        raise InvalidInput("min_price", "Minimum price cannot be negative.")
    if max_price is not None and max_price < 0:
        raise InvalidInput("max_price", "Maximum price cannot be negative.")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise InvalidInput("max_price", "Maximum price cannot be lower than minimum price.")
    if rooms is not None and rooms <= 0:
        raise InvalidInput("rooms", "Number of rooms must be greater than 0.")

    # A listing row only stores flat_id. Number of rooms and the flat's archived_at live in the flat table.
    # join glues each listing row to its own flat row (listing.flat_id = flat.id, known from the
    # relationship in models.py), so where() can filter on Flat columns too. Without it, Postgres would
    # pair every listing with every flat and return wrong rows.
    # contains_eager fills listing.flat from that same join, so the caller can read listing.flat
    # without another query. joinedload would add a second, separate join of the flat table.
    query = (select(Listing).join(Listing.flat).options(contains_eager(Listing.flat))
             .where(Listing.taken_at==None, Listing.archived_at==None, Flat.archived_at==None))
    if min_price is not None:
        query = query.where(min_price <= Listing.price)
    if max_price is not None:
        query = query.where(max_price >= Listing.price)
    if rooms is not None:
        query = query.where(Flat.number_of_rooms == rooms)

    query = query.order_by(Listing.published_at.desc())
    listings = session.scalars(query).all()

    return listings
