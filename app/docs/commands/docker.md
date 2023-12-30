# Docker Commands

Download the image from [DockerHub](https://hub.docker.com/r/jiisanda/docflow).

OR

```commandline
docker pull jiisanda/docflow
```

### Get all containers
```commandline
docker ps
```

### Docker-compose up
For development, following  will by default reads two files, a `docker-compose.yml` and an optional 
`docker-compose.override.yml` file.
```commandline
docker-compose up
```
For production, you can use the `-f` option to specify the files to use.
```commandline
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```
### docker-compose up in detach mode
```commandline
docker-compose up -d
```

### Building an image
Build an image if there are changes in the code
```commandline
docker-compose up --build
```

### Stopping/Deleting all containers
```commandline
docker-compose down
```


### To access databases created inside docker container of docflow
```commandline
docker exec -it <postgres_container_id> psql -U <username>
```
