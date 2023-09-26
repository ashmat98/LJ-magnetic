
create function pg_temp.roundn(val double precision, n integer)
returns numeric
language plpgsql
as
$$
declare
begin
    RETURN round(val*POWER(10, n))/POWER(10, n);
end;
$$;

-- DROP FUNCTION IF EXISTS tostr(double precision, double precision, integer);

create function pg_temp.tostr(val1 double precision, val2 double precision, n integer)
returns TEXT
language plpgsql
as
$$
declare
begin
   
    IF pg_temp.roundn(val1, n) = pg_temp.roundn(val2, n) THEN
        return pg_temp.roundn(val1, n);
    ELSE
        return pg_temp.roundn(val1, n) || '-' || pg_temp.roundn(val2, n);
    END IF;
end;
$$;

select 
group_name,
pg_temp.tostr(min(eccentricity), max(eccentricity), 2) AS eccentricity,
pg_temp.tostr(min(particles),max(particles),2) as N,
pg_temp.tostr(min(iterations)*AVG(record_interval), max(iterations)*AVG(record_interval),0)  as t,
pg_temp.tostr(min("L_init"), max("L_init"),3)  as "L_init",
pg_temp.tostr(min(iterations), max(iterations),0)  as iterations,
count(id),
CASE
    when group_name = 'ER 6.1' then 'check_diffusion; changing sigma to check diffusion hypothesis of L'
    when group_name = 'ER 6.2' then 'check_diffusion; same as ER 6.1 with more particles'
    when group_name = 'ER 6.3' then 'allow initial relaxation for 200 time unit'
    when group_name = 'ER 3.2' then 'sigma 0.15 with warmup'
    when group_name = 'ER 2' then 'eccentricity 0.2 faster relaxation'
    when group_name = 'ER 3.1' then 'sigma 0.1 with warmup'
    when group_name = 'ER 3' then 'sigma 0.1'
    when group_name = 'ER 5' then 'check_diffusion; without warmup'
    when group_name = 'Ensemble 5.1' then 'random grid, to check theoretical dependencied f_omega and f_beta'
    when group_name = 'Ensemble 5.1.lammps' then 'same as Ensemble 5.1, but with lammps engine'
    when group_name = 'Ensemble 4' then 'long and small dt simulation. 100 copies with same parameter'
    when group_name = 'CtR 6.2' then 'compare to rotation'
    when group_name = 'Ensemble 9' then 'relaxation finder'
    when group_name = 'Ensemble 9.1' then 'relaxation finder - finer, complement to ensemble 9'
    when group_name = 'GE 1.0' then 'grid of parameters (T, Omega) for gamma estimation'
    when group_name = 'GE 2.2' then 'finer grid'
    -- Add more WHEN clauses for other key-value mappings
    ELSE ''
END AS mapped_column
from simulation 
WHERE  group_name not in (
    'ER 6','GE 2.0',
    'Test Ensemble 1','ER 3.3-draft','CtR 6.2 debug', 'Ensemble 5', 'Ensemble 6', 'Ensemble 7', 'Ensemble 8')
group by group_name 
ORDER BY group_name ASC;

