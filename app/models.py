from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="Active")

    staff_profile = relationship("StaffProfile", back_populates="user", uselist=False)
    bookings = relationship("Booking", back_populates="user")


class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    staff_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    contact_details = Column(String(255))
    status = Column(String(20), nullable=False, default="Active")

    user = relationship("User", back_populates="staff_profile")
    treks = relationship("Trek", back_populates="assigned_staff")


class Trek(Base):
    __tablename__ = "treks"

    trek_id = Column(Integer, primary_key=True)
    trek_name = Column(String(120), nullable=False)
    location = Column(String(120), nullable=False)
    difficulty = Column(String(20), nullable=False)
    duration_days = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("staff_profiles.staff_id"))
    status = Column(String(20), nullable=False, default="Pending")
    start_date = Column(Date)
    end_date = Column(Date)

    assigned_staff = relationship("StaffProfile", back_populates="treks")
    bookings = relationship("Booking", back_populates="trek")


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    trek_id = Column(Integer, ForeignKey("treks.trek_id"), nullable=False)
    booking_date = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(String(20), nullable=False, default="Booked")
    payment_status = Column(String(20))

    user = relationship("User", back_populates="bookings")
    trek = relationship("Trek", back_populates="bookings")
