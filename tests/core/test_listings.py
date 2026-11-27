from app.core.listings import create_flat, create_listing, get_listing, list_listings
from app.core.errors import InvalidInput
from sqlalchemy import func
import pytest
from datetime import datetime, timezone

def make_listing(session, landlord, neighbourhood, number_of_rooms, price):
    flat = create_flat(session=session, landlord_id=landlord.user_id, area_m2=56.00,
                       number_of_rooms=number_of_rooms, street="Test street",
                       house_number="10", parking_type="Private parking", neighbourhood_id=neighbourhood.id,
                       longitude=18.6939, latitude=45.5511)
    listing = create_listing(session=session, flat_id=flat.id, price=price,
                             description="This is test description", utilities_included=False)

    return listing

def test_create_flat_saves_valid_flat(session, landlord, neighbourhood):
    flat = create_flat(session=session, landlord_id=landlord.user_id, area_m2=56.00,
                       number_of_rooms=2, street="Test street", house_number="10",
                       parking_type="Private parking", neighbourhood_id=neighbourhood.id,
                       longitude=18.6939, latitude=45.5511)
    
    assert flat.id is not None

def test_create_flat_rejects_zero_area(session, landlord, neighbourhood):
    # The code in this block must raise InvalidInput. Catch it and store it in error_info.
    with pytest.raises(InvalidInput) as error_info:
        create_flat(session=session, landlord_id=landlord.user_id, area_m2=0.00,
                    number_of_rooms=2, street="Test street", house_number="10",
                    parking_type="Private parking", neighbourhood_id=neighbourhood.id,
                    longitude=18.6939, latitude=45.5511)
    assert error_info.value.field == "area_m2"

def test_create_listing_saves_valid_listing(session, flat):
    listing = create_listing(session=session, flat_id=flat.id, price=200.00,
                             description="This is test description", utilities_included=False)

    assert listing.id is not None

def test_create_listing_rejects_zero_price(session, flat):
    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=0.00,
                            description="This is test description", utilities_included=False)

    assert error_info.value.field == "price"

def test_create_listing_rejects_empty_description(session, flat):
    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=200.00,
                            description="", utilities_included=False)

    assert error_info.value.field == "description"

def test_create_listing_rejects_missing_flat(session):
    with pytest.raises(InvalidInput) as error_info:
        # Pass made-up flat_id (flat which doesn't exist)
        create_listing(session=session, flat_id=99999, price=200.00,
                            description="This is test description", utilities_included=False)

    assert error_info.value.field == "flat_id"

def test_create_listing_rejects_archived_flat(session, flat):
    flat.archived_at = func.now()
    session.commit()

    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=200.00,
                            description="This is test description", utilities_included=False)

    assert error_info.value.field == "flat_id"

def test_create_listing_rejects_non_bool_utilities(session, flat):
    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=200.00,
                            description="This is test description", utilities_included="Yes")

    assert error_info.value.field == "utilities_included"

def test_get_listing_finds_listing_by_id(session, listing):
    found_listing = get_listing(session=session, listing_id=listing.id)

    assert found_listing.id == listing.id

def test_get_listing_loads_flat(session, listing, flat):
    found_listing = get_listing(session=session, listing_id=listing.id)

    assert found_listing.flat.id == flat.id

def test_get_listing_returns_none_for_missing_id(session, listing):
    # Pass made-up listing_id (listing which doesn't exist)
    found_listing = get_listing(session=session, listing_id=9999)

    assert found_listing is None

def test_list_listings_returns_only_open_listings(session, landlord, neighbourhood):
    open_listing = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=1, price=100)
    taken_listing = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=2, price=200)
    taken_listing.taken_at = func.now()
    archived_listing = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=3, price=300)
    archived_listing.archived_at = func.now()
    listing_with_archived_flat = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=4, price=400)
    listing_with_archived_flat.flat.archived_at = func.now()

    session.commit()

    listings = list_listings(session)

    assert len(listings) == 1 and open_listing in listings

def test_list_listings_min_price_includes_its_value(session, landlord, neighbourhood):
    listing_100 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=1, price=100)
    listing_200 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=2, price=200)
    listing_300 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=3, price=300)

    listings = list_listings(session=session, min_price=200)

    assert len(listings) == 2 and listing_200 in listings and listing_300 in listings

def test_list_listings_max_price_includes_its_value(session, landlord, neighbourhood):
    listing_100 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=1, price=100)
    listing_200 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=2, price=200)
    listing_300 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=3, price=300)

    listings = list_listings(session=session, max_price=200)

    assert len(listings) == 2 and listing_100 in listings and listing_200 in listings

def test_list_listings_equal_min_and_max_price_return_exact_listing(session, landlord, neighbourhood):
    listing_100 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=1, price=100)
    listing_200 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=2, price=200)
    listing_300 = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=3, price=300)

    listings = list_listings(session=session, min_price=200, max_price=200)

    assert len(listings) == 1 and listing_200 in listings

def test_list_listings_rooms_matches_exactly(session, landlord, neighbourhood):
    listing_1_room = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=1, price=100)
    listing_2_room = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=2, price=200)
    listing_3_room = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=3, price=300)

    listings = list_listings(session=session, rooms=2)

    assert len(listings) == 1 and listing_2_room in listings

def test_list_listings_returns_newest_first(session, landlord, neighbourhood):
    listing_middle = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=2, price=200)
    listing_middle.published_at = datetime(2026, 10, 27, tzinfo=timezone.utc)
    session.commit()

    listing_old = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=1, price=100)
    listing_old.published_at = datetime(2026, 5, 27, tzinfo=timezone.utc)
    session.commit()

    listing_new = make_listing(session=session, landlord=landlord, neighbourhood=neighbourhood,
                            number_of_rooms=3, price=300)
    listing_new.published_at = datetime(2026, 11, 27, tzinfo=timezone.utc)
    session.commit()

    listings = [listing_new, listing_middle, listing_old]
    expected_listings = list_listings(session=session)

    assert expected_listings == listings

def test_list_listings_rejects_negative_min_price(session):
    with pytest.raises(InvalidInput) as error_info:
        list_listings(session=session, min_price=-200)

    assert error_info.value.field == "min_price" 

def test_list_listings_rejects_min_price_above_max_price(session):
    with pytest.raises(InvalidInput) as error_info:
        list_listings(session=session, min_price=500, max_price=100)

    assert error_info.value.field == "max_price" 

def test_list_listings_rejects_zero_rooms(session):
    with pytest.raises(InvalidInput) as error_info:
        list_listings(session=session, rooms=0)

    assert error_info.value.field == "rooms" 

