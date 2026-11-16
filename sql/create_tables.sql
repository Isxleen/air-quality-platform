CREATE SCHEMA IF NOT EXISTS public;


CREATE TABLE IF NOT EXISTS public.cities (
    city_name  TEXT PRIMARY KEY,
    latitude   DOUBLE PRECISION NOT NULL,
    longitude  DOUBLE PRECISION NOT NULL
);
 
CREATE TABLE IF NOT EXISTS public.air_quality (
    city_name         TEXT        NOT NULL REFERENCES public.cities (city_name),
    date              TIMESTAMPTZ NOT NULL,
    pm10              REAL,  
    pm2_5             REAL,  
    carbon_monoxide   REAL,  
    nitrogen_dioxide  REAL,  
    sulphur_dioxide   REAL,  
    ozone             REAL,  
    european_aqi      REAL,   
    PRIMARY KEY (city_name, date)
);
 