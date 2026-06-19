from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

"""Database url generally follows this structure 
databasedriver://username:password@hostname:port/<databasename>"""
DATABASE_URL="sqlite:///./tasks.db"

"""Used to create an engine.. a pool of connections to the specified database ur with some connect_arguments"""
engine=create_engine(DATABASE_URL,connect_args={"check_same_thread": False})

"""Used to create sessions for the specified engine with default args."""
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)


"""Base class for all the ORM(Object Relation Mapper) classes"""
Base=declarative_base()

""" to create a db session and automatically close the session whatever happens .. or else it will throw error... """
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
