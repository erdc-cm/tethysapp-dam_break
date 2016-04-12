# Put your persistent store initializer functions in here
from .model import engine, SessionMaker, Base, Dam

def init_dam_info_db(first_time):
    """
    Initialize dam info database
    """
    # Create tables
    Base.metadata.create_all(engine)
    
    # Initial data
    if first_time:
        # Make session
        session = SessionMaker()

        # Dam
        dam1 = Dam(latitude=40.406624,
                   longitude=-111.529133,
                   peak_flow=1000,
                   time_peak=3,
                   peak_duration=1,
                   falling_limb_duration=96)


        session.add(dam1)

        session.commit()
        session.close()