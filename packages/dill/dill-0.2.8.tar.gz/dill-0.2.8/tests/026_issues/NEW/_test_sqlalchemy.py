from sqlalchemy import Column, Integer, String, DateTime, Float,\
    ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from datetime import datetime

def connect_db(username, password, db_name, host='localhost', port=3306,
               echo=True):
    """ This function wraps the create_engine from SQLA in order to be more
    user friendly

    Args:
        host(string):       The url of the database
        username(string):   The username to login to the database
        password(string):   The password to login to the database
        db_name(string):    The name of the database
        host(string):       The host (URL) where the DB resides
                                (default:localhost)
        port(int):          The port where the DB is listening (default:3306)
        echo(bool):         If SQL statements must be echoed or not
                                (default:true)

    Return:
        db(Engine):         The Engine instance to the database

    """
    DB_STRING = 'mysql+mysqldb://{user}:{pwd}@{host}:{port}/{db_name}'

    return create_engine(DB_STRING.format(
        user=username,
        pwd=password,
        host=host,
        port=port,
        db_name=db_name,
    ), echo=echo)

Base = declarative_base()


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    readings = relationship("Reading", backref='sensor',
                            cascade='all, delete-orphan')

    def __init__(self, name):
        self.name = name

    def read(self, room):
        return [
            Reading(
                self,
                room,
                datetime.now(),
                10.0),

            Reading(
                self,
                room,
                datetime.now(),
                20.0),

            Reading(
                self,
                room,
                datetime.now(),
                30.0)
        ]


class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    readings = relationship("Reading", backref='room',
                            cascade='all, delete-orphan')

    def __init__(self, name):
        self.name = name


class Reading(Base):
    __tablename__ = 'reading'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    voltage = Column(Float)

    sensor_id = Column(Integer, ForeignKey('sensor.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)

    def __init__(self, sensor, room, date, voltage):
        self.sensor = sensor
        self.room = room
        self.date = date
        self.voltage = voltage

    def __repr__(self):
        return '<Read {} {}>'.format(self.date, self.voltage)


if __name__ == '__main__':

    db = connect_db(
        username='test',
        password='test',
        db_name='test_db',
        echo=False)

    Base.metadata.create_all(db)
    S = sessionmaker(db)
    session = S()

    def mp_read(room):
        sensor = Sensor('Pressure Sensor')

        return sensor.read(room)

    # readings = sensor.read(room)

    # import multiprocessing as mpp
    import pathos.multiprocessing as mpp
    pool = mpp.ProcessingPool(2)
    # pool = mpp.Pool(2)

    rooms = [Room('bedroom'), Room('Living'), Room('kitchen')]
    sensor = Sensor('Pressure Sensor')
    readings = pool.map(mp_read, rooms)

    # session.add(sensor)
    # session.commit()


"""
This gives no errors with multiprocessing but raises:
pickle.PicklingError: Can't pickle <class 'sqlalchemy.ext.declarative.api.Base'>: it's not found as sqlalchemy.ext.declarative.api.Base if using pathos.multiprocessing
"""
