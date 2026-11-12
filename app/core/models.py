from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, false, func, MetaData, ForeignKey, Numeric, CheckConstraint, UniqueConstraint
from datetime import datetime
from geoalchemy2 import Geography, WKBElement
from decimal import Decimal

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",        
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

class Student(Base):
    __tablename__= "student"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"))

class Landlord(Base):
    __tablename__= "landlord"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

class Flat(Base):
    __tablename__= "flat"
    __table_args__=(
        CheckConstraint("area_m2 > 0", name="area"),
        CheckConstraint("number_of_rooms > 0", name="number_of_rooms"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    landlord_id: Mapped[int] = mapped_column(ForeignKey("landlord.user_id"), index=True)
    area_m2: Mapped[Decimal] = mapped_column(Numeric(6,2))
    number_of_rooms: Mapped[int] = mapped_column()
    street: Mapped[str] = mapped_column(String(50))
    house_number: Mapped[str] = mapped_column(String(10))
    floor: Mapped[int | None] = mapped_column()
    unit : Mapped[str | None] = mapped_column(String(10))
    parking_type: Mapped[str] = mapped_column(String(20))
    neighbourhood_id: Mapped[int] = mapped_column(ForeignKey("neighbourhood.id"), index=True)
    location: Mapped[WKBElement] = mapped_column(Geography(geometry_type='POINT', srid=4326))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Listing(Base):
    __tablename__= "listing"
    __table_args__= (
        CheckConstraint("price > 0", name="price"),
        CheckConstraint("taken_at IS NULL OR archived_at IS NULL", name="taken_or_archived"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    flat_id: Mapped[int] = mapped_column(ForeignKey("flat.id"),index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(8,2))
    utilities_included: Mapped[bool] = mapped_column(server_default=false())
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    description: Mapped[str] = mapped_column(String(1000))

class Review(Base):
    __tablename__= "review"
    __table_args__=(
        CheckConstraint("rating BETWEEN 1 AND 5", name="rating"),
        UniqueConstraint("student_id", "flat_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column()
    description: Mapped[str] = mapped_column(String(1000))
    student_id: Mapped[int | None] = mapped_column(ForeignKey("student.user_id", ondelete="SET NULL"))
    flat_id: Mapped[int] = mapped_column(ForeignKey("flat.id", ondelete="RESTRICT"), index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hidden_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

class Report(Base):
    __tablename__= "report"
    __table_args__=(
        UniqueConstraint("review_id", "reporter_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("review.id"))
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

class ListingPhoto(Base):
    __tablename__= "listing_photo"
    __table_args__=(
        UniqueConstraint("listing_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listing.id"))
    file_key: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
