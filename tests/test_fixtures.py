from app.core.models import Neighbourhood
from sqlalchemy import select

def test_session_saves_and_reads_rows(session):
    new_neighbourhood = Neighbourhood(name="Testno naslje")
    session.add(new_neighbourhood)
    session.commit()

    query = select(Neighbourhood).where(Neighbourhood.name == "Testno naslje")
    found_neighbourhood = session.scalars(query).first()

    assert found_neighbourhood is not None