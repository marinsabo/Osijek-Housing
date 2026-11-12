from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, false, func, MetaData
from datetime import datetime
from geoalchemy2 import Geography, WKBElement

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })

class User(Base):
    __tablename__= "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    is_moderator: Mapped[bool] = mapped_column(server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Neighbourhood(Base):
    __tablename__= "neighbourhood"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

class Faculty(Base):
    __tablename__= "faculty"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    location: Mapped[WKBElement] = mapped_column(Geography(geometry_type='POINT', srid=4326))
    email_domain: Mapped[str] = mapped_column(String(50), unique=True)

class LoginCode(Base):
    __tablename__= "login_code"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(server_default="0")
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


'''
class Student(Base):
    __tablename__= "student"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column()

class Landlord(Base):
    __tablename__= "landlord"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[int] = mapped_column()

class Flat(Base):
    __tablename__= "flat"

    id: Mapped[int] = mapped_column(primary_key=True)

'''