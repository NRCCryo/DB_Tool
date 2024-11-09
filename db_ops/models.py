# db_ops/models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class Test(Base):
    __tablename__ = 'tests'
    test_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    wip_id = Column(Integer, ForeignKey('wips.wip_id'))
    wip = relationship("WIP", back_populates="tests")

class Coldhead(Base):
    __tablename__ = 'coldheads'
    coldhead_id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String, unique=True, nullable=False)
    # Add other relevant fields as needed

    # Relationship to WIP
    wips = relationship("WIP", back_populates="coldhead")

class Displacer(Base):
    __tablename__ = 'displacers'
    displacer_id = Column(Integer, primary_key=True, autoincrement=True)
    displacer_serial_number = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    initial_open_date = Column(Date, nullable=True)
    # Add other relevant fields as needed

    # Relationship to WIP
    wips = relationship("WIP", back_populates="displacer")


class WIP(Base):
    __tablename__ = 'wips'
    wip_id = Column(Integer, primary_key=True, autoincrement=True)
    coldhead_id = Column(Integer, ForeignKey('coldheads.coldhead_id'), nullable=False)
    displacer_id = Column(Integer, ForeignKey('displacers.displacer_id'), nullable=False)
    wip_number = Column(String, nullable=False, unique=True)
    arrival_date = Column(Date, nullable=True)
    teardown_date = Column(Date, nullable=True)
    status = Column(String, nullable=True)

    # Relationships
    coldhead = relationship("Coldhead", back_populates="wips")
    displacer = relationship("Displacer", back_populates="wips")
    tests = relationship("Test", back_populates="wip")
