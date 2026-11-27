from app.core.listings import create_flat
from app.core.errors import InvalidInput
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
    assert "area_m2" == error_info.value.field
