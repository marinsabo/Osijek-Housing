from app.core.database import SessionLocal
from app.core.errors import InvalidInput
from app.core.listings import create_flat
from app.core.models import User, Landlord, Neighbourhood

with SessionLocal() as session:
    user = User(first_name = "Marin", last_name = "Sabo", email = "sabo221@gmail.com")
    session.add(user)
    session.commit()
    session.refresh(user)

    landlord = Landlord(user_id = user.id, phone_number = "+385955092855")
    neighbourhood = Neighbourhood(name = "Jug")

    session.add(landlord)
    session.add(neighbourhood)
    session.commit()
    session.refresh(landlord)
    session.refresh(neighbourhood)

    flat = create_flat(session, landlord.user_id, 56.00, 2, "Vijenac Ivana Meštrovića", "4", 
                "Garaža", neighbourhood.id, 18.695515, 45.554962, 2)

    print(flat.id)

    try:  flat = create_flat(session, landlord.user_id, 0.00, 2, "Vijenac Ivana Meštrovića", "4", 
                    "Garaža", neighbourhood.id, 18.695515, 45.554962, 2)
    except InvalidInput as e:
        print(e.field, e.message)