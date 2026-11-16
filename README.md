# Poland Air Quality Data Platform

A data engineering project that collects, stores and analyses air quality data for several Polish cities, using weather conditions as explanatory variables.

> **Status: Work in progress.** Phase 1 (air quality ingestion) is complete. Weather data integration and the remaining pipeline stages are planned.

## Research question

Do Polish cities show different pollution patterns depending on the season and weather conditions?

The project aims to explore how air pollution varies across cities and throughout the year, and whether meteorological conditions such as temperature, humidity, wind and precipitation help explain these variations.

## Cities

The project currently covers seven Polish cities:

- Warsaw
- Kraków
- Wrocław
- Gdańsk
- Poznań
- Katowice
- Łódź

## Data sources and limitations

### Air quality

[Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), based on the CAMS (Copernicus Atmosphere Monitoring Service) model.

### Weather (planned)

[Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), based on ERA5 reanalysis.

### Data limitations

- The air quality data is **modelled**, not measured directly by ground monitoring stations. It is not equivalent to official monitoring data from the Polish Chief Inspectorate for Environmental Protection (GIOŚ).
- The spatial resolution is several kilometres, so local differences between neighbourhoods are not captured.
- Historical data availability depends on the underlying dataset (reanalysis or forecast).
- The model used, available date range and temporal resolution for the loaded period will be documented as the project develops.

## Variables

### Air quality

| Variable | Description | Unit |
|---|---|---|
| `pm10` | Inhalable particles | µg/m³ |
| `pm2_5` | Fine particles | µg/m³ |
| `carbon_monoxide` | Carbon monoxide | µg/m³ |
| `nitrogen_dioxide` | Nitrogen dioxide (traffic) | µg/m³ |
| `sulphur_dioxide` | Sulphur dioxide (industry) | µg/m³ |
| `ozone` | Ozone | µg/m³ |
| `european_aqi` | European Air Quality Index | Index (no unit) |

All air quality values are hourly.

### Weather (planned)

The following meteorological variables are planned:

- Temperature
- Relative humidity
- Wind speed
- Precipitation
- Atmospheric pressure

These variables will be used to investigate possible relationships between weather conditions and air pollution.

## Architecture

### Current architecture

```text
Open-Meteo API
      |
      v
Python (extraction and loading)
      |
      v
PostgreSQL
```

The current setup uses Docker to run PostgreSQL and the ingestion job in separate containers.

### Target architecture

As the project evolves, the pipeline will follow a Medallion-style architecture:

```text
Open-Meteo APIs
      |
      v
Data ingestion (Python)
      |
      v
Bronze layer (raw data)
      |
      v
Silver layer (cleaned and validated data)
      |
      v
Gold layer (analytical datasets)
      |
      v
PostgreSQL / Parquet
      |
      v
Analysis and visualisation
```

Airflow will be introduced later to orchestrate and schedule the pipeline.

## Project structure

```text
air-quality-platform/
├── config/
│   └── config.yaml                # cities, table names, optional date range
├── sql/
│   ├── create_tables.sql          # tables, primary and foreign keys
│   └── check_load.sql             # sanity checks after a load
├── src/
│   └── air_quality_platform/
│       └── ingestion/
│           └── air_quality_api.py # extraction and loading
├── utility/
│   ├── constants.py               # cities, variables, config keys
│   └── utils.py                   # config loading, database connection
├── data/                          # bronze / silver / gold layers (future phases)
├── tests/
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Database model

The current PostgreSQL database contains two tables:

- `cities (city_name PK, latitude, longitude)`
- `air_quality (city_name FK, date, pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone, european_aqi)`

The primary key of the `air_quality` table is `(city_name, date)`, preventing duplicate rows when the same period is loaded more than once.

## How to run

### 1. Configure environment variables

Copy the environment template and add your database credentials:

```bash
cp .env.example .env
```

### 2. Start the database and run ingestion

```bash
docker compose up --build
```

The database tables are created automatically when PostgreSQL starts for the first time, using `sql/create_tables.sql`.

### 3. Check the data load

```bash
docker compose exec -T db psql -U <DB_USER> -d <DB_NAME> < sql/check_load.sql
```

### Historical load vs daily load

The ingestion behaviour is controlled through `config/config.yaml`:

- When `start_date` and `end_date` are configured under `air_quality_data`, the pipeline loads the specified historical period.
- When no date range is provided, the pipeline loads data for the current day in Polish local time.

To start from scratch and remove the database volume:

```bash
docker compose down -v
```

**Note:** This command deletes the persisted database data.

## Roadmap

The project is being developed in the following phases:

- **Phase 1 – Air quality ingestion:** Open-Meteo extraction, seven cities, historical and daily loads, PostgreSQL and Docker. Completed.
- **Phase 1 – Weather ingestion:** Extract temperature, humidity, wind, precipitation and pressure.
- **Phase 2 – Data processing and storage:** Data cleaning, validation, Bronze / Silver / Gold layers, Parquet storage and automated tests.
- **Phase 3 – Pipeline orchestration:** Airflow integration, scheduled executions, retries and duplicate prevention.
- **Phase 4 – Data analysis:** Exploratory data analysis, seasonal patterns, weather correlations and anomaly detection.
- **Phase 5 – Visualisation and machine learning:** Build a dashboard using Streamlit or Power BI and develop a PM2.5 prediction model.

## Possible future improvements

- Compare modelled air quality data with real measurements from the GIOŚ API.
- Introduce dbt for SQL-based transformations.
- Improve data quality checks and pipeline monitoring.

## Tech stack

- **Language:** Python
- **Data processing:** pandas
- **API:** Open-Meteo
- **Database:** PostgreSQL
- **Database connectivity:** SQLAlchemy
- **Containers:** Docker and Docker Compose
- **Dependency management:** uv
- **Orchestration (planned):** Apache Airflow
- **Storage (planned):** Parquet
- **Visualisation (planned):** Streamlit or Power BI
- **Transformations (possible future improvement):** dbt

## Results

*Coming soon.*

The final results will include an analysis of air quality patterns across the seven cities, seasonal variations and the relationship between pollution levels and weather conditions.