import logging
import os

import yaml
from sqlalchemy import create_engine, text

from utility.constants import DATABASE, DB_CONNECTION_URL, POSTGRES_USER, POSTGRES_PASSWORD

#Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    """ Load configuration from YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_db_engine(db_connection_url):
    """Create and return a SQLAlchemy database engine."""
    logger.info("Creating database engine...")

    engine = create_engine(
        db_connection_url,
        pool_pre_ping=True,
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT version()"))

        logger.info("PostgreSQL connection successful!")

        return engine

    except Exception:
        engine.dispose()
        logger.exception("PostgreSQL connection failed.")
        raise   

def get_db_connection(config):
    """Build the database connection URL from configuration and environment variables."""
    db_username = os.getenv(POSTGRES_USER)
    db_password = os.getenv(POSTGRES_PASSWORD)

    if not db_username or not db_password:
        raise ValueError("Database credentials are missing from environment variables.")

    db_connection_url_template = config[DATABASE][DB_CONNECTION_URL]

    db_connection_url = db_connection_url_template.format(
        username=db_username,
        password=db_password,
    )

    return db_connection_url
