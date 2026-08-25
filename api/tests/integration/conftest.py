import os
import tempfile

# Point the app at an isolated throwaway SQLite DB *before* importing it, so the
# smoke tests never touch a real/seeded database. Must run before `main` import.
_TEST_DB = os.path.join(tempfile.gettempdir(), "pokeanalytics_test.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB}")
os.environ.setdefault("AUTO_SEED", "0")
os.environ.pop("SEED_TOKEN", None)

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(scope="session")
def client():
    # The `with` block runs the lifespan, which creates the tables.
    with TestClient(main.app) as c:
        yield c
