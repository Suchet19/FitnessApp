import pytest
from app.database import Base, engine

@pytest.fixture(autouse=True, scope="function")
def clean_database():
    # Reset database state for every test.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield