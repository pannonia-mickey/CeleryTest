import datetime
from uuid import uuid4

from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class OrderRecord(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    order_id = Column(String, unique=True)

class InvoiceRecord(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    invoice_ref = Column(String, index=True)
    invoice_id = Column(String, unique=True)

class PaymentRecord(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    invoice_id = Column(String, index=True)
    payment_id = Column(String, unique=True)

class ErrorRecord(Base):
    __tablename__ = "errors"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    message = Column(String)

Base.metadata.create_all(bind=engine)
