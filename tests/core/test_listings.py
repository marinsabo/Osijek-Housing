from app.core.listings import create_flat, create_listing
from app.core.errors import InvalidInput
from sqlalchemy import func
import pytest

def test_create_flat_saves_valid_flat(session, landlord, neighbourhood):
    flat = create_flat(session=session, landlord_id=landlord.user_id, area_m2=56.00,
                       number_of_rooms=2, street="Test street", house_number="10",
                       parking_type="Private parking", neighbourhood_id=neighbourhood.id,
                       longitude=18.6939, latitude=45.5511)
    
    assert flat.id is not None

def test_creating_flat_rejects_zero_area(session, landlord, neighbourhood):
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

def test_creating_listing_rejects_zero_price(session, flat):
    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=0.00,
                            description="This is test description", utilities_included=False)

    assert error_info.value.field == "price"

def test_creating_listing_rejects_empty_description(session, flat):
    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=200.00,
                            description="", utilities_included=False)

    assert error_info.value.field == "description"

def test_creating_listing_rejects_nonexistent_flat(session):
    with pytest.raises(InvalidInput) as error_info:
        # Pass made-up flat_id (flat which doesn't exist)
        create_listing(session=session, flat_id=99999, price=200.00,
                            description="This is test description", utilities_included=False)

    assert error_info.value.field == "flat_id"

def test_creating_listing_rejects_archived_flat(session, flat):
    flat.archived_at = func.now()
    session.commit()

    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=200.00,
                            description="This is test description", utilities_included=False)

    assert error_info.value.field == "flat_id"

def test_creating_listing_rejects_not_bool_utilities_included(session, flat):
    with pytest.raises(InvalidInput) as error_info:
        create_listing(session=session, flat_id=flat.id, price=200.00,
                            description="This is test description", utilities_included="Yes")

    assert error_info.value.field == "utilities_included"
