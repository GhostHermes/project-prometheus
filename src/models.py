from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between Commune and Asset
commune_asset = Table('commune_asset', Base.metadata,
    Column('commune_id', Integer, ForeignKey('communes.id')),
    Column('asset_id', Integer, ForeignKey('assets.id'))
)

class Commune(Base):
    __tablename__ = 'communes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("User", back_populates="commune")
    assets = relationship("Asset", secondary=commune_asset, back_populates="communes")
    projects = relationship("Project", back_populates="commune")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    commune_id = Column(Integer, ForeignKey('communes.id'))
    
    commune = relationship("Commune", back_populates="members")

class Asset(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50))  # e.g., "equipment", "intellectual property", "real estate"
    value = Column(Integer)  # Monetary value in cents
    
    communes = relationship("Commune", secondary=commune_asset, back_populates="assets")

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20))  # e.g., "planning", "in progress", "completed"
    commune_id = Column(Integer, ForeignKey('communes.id'))
    
    commune = relationship("Commune", back_populates="projects")