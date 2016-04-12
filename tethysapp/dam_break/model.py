# Put your persistent store models in this file
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import sessionmaker

from .app import DamBreak

# DB Engine, sessionmaker and base
engine = DamBreak.get_persistent_store_engine('dam_info_db')
SessionMaker = sessionmaker(bind=engine)
Base = declarative_base()

# SQLAlchemy ORM definition for the dam_info table
class Dam(Base):
    '''
    SQLAlchemy Dam DB Model
    '''
    __tablename__ = 'dam'

    # Columns
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    peak_flow = Column(Float)
    time_peak = Column(Float)
    peak_duration = Column(Float)
    falling_limb_duration = Column(Float)

    def __init__(self, latitude, 
                 longitude, 
                 peak_flow,
                 time_peak,
                 peak_duration,
                 falling_limb_duration):
        """
        Constructor for a dam model
        """
        self.latitude = latitude
        self.longitude = longitude
        self.peak_flow = peak_flow
        self.time_peak = time_peak
        self.peak_duration = peak_duration
        self.falling_limb_duration = falling_limb_duration