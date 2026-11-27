from app.core.models import Neighbourhood, User, Landlord
from app.core.listings import create_flat
import pytest

@pytest.fixture()
def neighbourhood(session):
    new_neighbourhood = Neighbourhood(name="Test neighbourhood")
    session.add(new_neighbourhood)
    session.commit()
    session.refresh(new_neighbourhood)

    return new_neighbourhood

@pytest.fixture()
def landlord(session):
    new_user = User(first_name="Jon", last_name="Jones", email="jonjones@example.com")
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    new_landlord = Landlord(user_id=new_user.id, phone_number="+385999999999")
    session.add(new_landlord)
    session.commit()
    session.refresh(new_landlord)

    return new_landlord

@pytest.fixture()
def flat(session, landlord, neighbourhood):
    new_flat = create_flat(session=session, landlord_id=landlord.user_id, area_m2=56.00,
                          number_of_rooms=2, street="Test street", house_number="10",
                          parking_type="Private parking", neighbourhood_id=neighbourhood.id,
                          longitude=18.6939, latitude=45.5511)

    return new_flat