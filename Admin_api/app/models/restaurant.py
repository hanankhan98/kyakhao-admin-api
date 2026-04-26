from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    # Business Details
    business_name = Column(String, nullable=False)
    tax_id = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    address = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)

    # Personal Details
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    description = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    banner = Column(String, nullable=True)

    # Bank Details
    bank_name = Column(String, nullable=True)
    account_holder_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)


    dishes = relationship("Dish", back_populates="restaurant")