Install Postgres locally
```
conda install -c anaconda postgresql
```

Initialize database, start the server
```
initdb -D ../pg_database
pg_ctl -D ../pg_database -l ../pg_logfile.log start -o "-F -p 54320" 
```

To stop the database, run
```
pg_ctl -D ../pg_database stop
```


Create superuser
```
createuser --encrypted --pwprompt ashmat
```

Using this superuser, create database
```
createdb --owner=ashmat lj_simulations
```

Connection string
```
psql -d lj_simulations -U ashmat -h localhost -p 5432
```