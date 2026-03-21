import logging
import os
import time

import connexion  # type: ignore
import connexion.mock  # type: ignore
import flask
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger(__name__)


def init_db(db_name):
    engine = create_engine(
        f"sqlite:///{db_name}.db", execution_options={"isolation_level": "AUTOCOMMIT"}
    )
    session_factory = scoped_session(sessionmaker(bind=engine))

    engine.dispose()
    return session_factory


def openapi_filenames() -> list[str]:
    return ["../openapi.yaml"]


def get_project_root_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "../")


def create_app(db_name: str = "app") -> connexion.FlaskApp:  # type: ignore[type-arg]
    logger.info("Starting API")

    db_session_factory = init_db(db_name)

    # Enable mock responses for unimplemented paths.
    resolver = connexion.mock.MockResolver(mock_all=False)

    app = connexion.FlaskApp(__name__)
    app.add_api(
        openapi_filenames()[0],
        resolver=resolver,
        strict_validation=True,
        validate_responses=True,
    )

    flask_app = app.app

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

    @flask_app.before_request
    def push_db():
        g.db = db_session_factory
        g.start_time = time.monotonic()
        g.connexion_flask_app = app

    @flask_app.teardown_request
    def close_db(exception=None):
        try:
            logger.debug("Closing DB session")
            db = g.pop("db", None)

            if db is not None:
                db.remove()
        except Exception:
            logger.exception("Exception while closing DB session")
            pass

    @flask_app.after_request
    def access_log_end(response):
        response_time_ms = 1000 * (time.monotonic() - g.get("start_time"))
        logger.info(
            "%s %s %s",
            response.status_code,
            flask.request.method,
            flask.request.full_path,
            extra={
                "remote_addr": flask.request.remote_addr,
                "response_length": response.content_length,
                "response_type": response.content_type,
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
            },
        )
        return response

    return app
