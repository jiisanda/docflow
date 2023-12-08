# PostgreSQL command

##### Connect to psql inside docker container
```commandline
docker exec -it <postgres_container_id> psql -U <username>
```

##### Lists all databases
```commandline
postgres-# \l
```

##### Connect to a postgres table
```commandline
postgres-# \c <database_name>
```

##### List of tables in database
```commandline
postgres-# \dt
```
