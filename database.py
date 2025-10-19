from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum

Base = declarative_base()

class UnitType(str, PyEnum):
    MACHINE = "machine"
    HASHBOARD = "hashboard"

class Assignee(Base):
    __tablename__ = 'assignees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

class Status(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), nullable=False, unique=True, index=True)

class RepairOrder(Base):
    __tablename__ = 'repair_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    received = Column(DateTime(timezone=True), nullable=True, index=True)
    finished = Column(DateTime(timezone=True), nullable=True, index=True)

    units = relationship("RepairUnit", back_populates="order")
    status = relationship("Status", foreign_keys=[status_id])

class RepairUnit(Base):
    __tablename__ = 'repair_units'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(20), unique=True, nullable=False, index=True)
    serial = Column(String(100), nullable=True)
    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    type = Column(SQLEnum(UnitType), nullable=False)
    current_status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    current_assignee_id = Column(Integer, ForeignKey('assignees.id'), nullable=True)
    repair_order_id = Column(Integer, ForeignKey('repair_orders.id'), nullable=False, index=True)
    
    events_json = Column(JSON, nullable=True)

    order = relationship("RepairOrder", back_populates="units")
    current_status = relationship("Status", foreign_keys=[current_status_id])
    current_assignee = relationship("Assignee", foreign_keys=[current_assignee_id])