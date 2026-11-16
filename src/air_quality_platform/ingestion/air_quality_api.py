import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import logging

from utility.constants import (
    TABLE_NAME,
    CITIES,
    SCHEMA_NAME,
    AIR_QUALITY_VARIABLES
)

from utility.utils import (
    load_config,
    get_db_engine,
    get_db_connection
)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"

#Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_cities_table(engine, schema_name):
    """Creates cities DataFrame and inserts it into the database"""
    logger.info("Creating cities Dataframe...")

    cities_df = pd.DataFrame.from_dict(
        {city_name: {"city_name": city_name, "latitude": coords["latitude"], "longitude": coords["longitude"]}
         for city_name, coords in CITIES.items()},
        orient='index'
    )

    try:
        # Insert cities into the specified schema
        cities_df.to_sql('cities', engine, if_exists='append', index=False, schema=schema_name)
        logger.info("Cities table created and data inserted successfully.")
    except IntegrityError:
        logger.warning("Cities already exist in the database.")

def fetch_air_quality_data(city_coords, openmeteo):
    """Fetch hourly air quality data for a city from Open-Meteo."""
    today = datetime.now(ZoneInfo("Europe/Warsaw")).date().isoformat()

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params={
        "latitude":city_coords["latitude"],
        "longitude":city_coords["longitude"],
        "hourly": AIR_QUALITY_VARIABLES,
        "start_date": today,
        "end_date": today,
        "timezone":"Europe/Warsaw"
    }

    api_response = openmeteo.weather_api(url, params=params)[0]
    logging.info(f"API response: {api_response}")
    logging.info(f"Hourly data: {api_response.Hourly()}")
    return api_response

def process_air_quality_data(openmeteo, cities, engine, schema_name, table_name):
   """Fetch and process air quality data for all cities."""
   air_quality_data_list = []
   for city_name, city_coords in cities.items():
        try:
            response = fetch_air_quality_data(city_coords, openmeteo)
            logger.info(f"Processing data for {city_name}...")
 
            hourly = response.Hourly()
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                ),
                "city_name": city_name
            }

            for i, var in enumerate(AIR_QUALITY_VARIABLES):
                hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()

            city_df = pd.DataFrame(data=hourly_data)
            air_quality_data_list.append(city_df)
            logger.info(f"{city_name}: {len(city_df)} rows collected.")

        except Exception as e:
            logger.error(f"Error processing data for city_name: {city_name}: {e}")

        #Insert data a


        # Combine all dataframes into one and insert into database
        if air_quality_data_list:
            air_quality_df = pd.concat(air_quality_data_list, ignore_index=True)
            try:
                air_quality_df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema_name)
                logger.info("Air quality data inserted succesfully")
            except IntegrityError:
                logger.warning("Air quality data already exists in database.")

def main():
    #Load config
    config = load_config(CONFIG_PATH)
    logger.info(f"Loaded configuration: {config}")

    db_connection_url = get_db_connection(config)

        #Access cities and table_name
    settings = config['air_quality']
    cities_data = settings['cities']
    table_name = settings['table_name']
    schema_name = config[SCHEMA_NAME]

    today = datetime.now(ZoneInfo("Europe/Warsaw")).date().isoformat()
    start_date = str(settings.get('start_date') or today)
    end_date = str(settings.get('end_date') or today)

    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) es posterior a end_date ({end_date})")

    #Create database engine
    engine = get_db_engine(db_connection_url)
    create_cities_table(engine, schema_name)

    #Set up the OpenMeteo API client
    logger.info("Setting up the Open-Meteo API client with cache and retry...")
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    logger.info(f"Loading air quality data from {start_date} to {end_date}...")
    process_air_quality_data(openmeteo, cities_data, engine, schema_name, table_name)

if __name__== "__main__":
    main()

