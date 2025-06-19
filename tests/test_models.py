import os
import sys

import pytest
from flask import Flask

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import ImportJob, db


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app


@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session


def test_import_job_defaults(session):
    job = ImportJob(filename="file.csv", total_rows=5)
    session.add(job)
    session.commit()
    assert job.status == "running"
    assert job.processed_rows == 0
