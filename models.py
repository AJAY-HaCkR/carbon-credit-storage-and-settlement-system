# models.py
from sqlalchemy import (Column, Integer, String, Float, DateTime, create_engine, func)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=False)
    cert_type = Column(String, nullable=False)
    unit_index = Column(Integer, nullable=False)  # index per unit
    status = Column(String, nullable=False, default="fresh")  # fresh, approved, burnt, rejected
    eth_rewarded = Column(Float, nullable=True, default=0.0)
    validator_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
    burnt_timestamp = Column(DateTime, nullable=True)

# Database helper
def create_session(db_path="sqlite:///certificates.db"):
    engine = create_engine(db_path, echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    return Session()

