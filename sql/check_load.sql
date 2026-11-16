SELECT city_name,
       count(*)                                AS filas,
       min(date)                               AS desde,
       max(date)                               AS hasta,
       count(*) FILTER (WHERE pm2_5 IS NULL)   AS pm2_5_nulos,
       round(avg(pm2_5)::numeric, 1)           AS pm2_5_medio
FROM public.air_quality
GROUP BY city_name
ORDER BY pm2_5_medio DESC;
 