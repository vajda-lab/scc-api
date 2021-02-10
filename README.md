# Read Me

### Docker Setup

Our Docker containers expect the existence of an environment file. To
generate it on *nix systems please invoke the `build_docker_env.sh`
script.

```shell
./build_docker_env.sh
```
To run the Docker containers use the command below.

```shell
docker-compose up
```

If you wish to run the servers in the background use the `-d`
(**d**etached) flag, as demonstrated below.

```shell
docker-compose up -d
```

To turn off the server use Control-C in the terminal window. If running
in the background use the command below.

```shell
docker-compose down
```

To remove all of the assets created by Docker to run the server use the
command below. The `--volumes` flag may be shortened to `-v`.
*NOTE* The command below will also remove the database, thus removing any records or users created. This includes the superuser.


```shell
docker-compose down --volumes --rmi local
```

To create a superuser use:
```shell 
docker-compose run django python manage.py createsuperuser
```


To run the tests in Docker use:

```shell
# from root of project
docker-compose run --rm django python manage.py test
```

### Non-Functioning commands (as of 2021-02-10)
These commands will be investigated & updated moving forward

To check PEP 8 for pre-commit use:
```shell
# from root of project
pre-commit run --all-files

```

To run Coverage:
```shell
# from root of project open Django container
docker exec -it gpcr-atlas_django_1 /bin/bash

# run in container
coverage run manage.py test

# open report in browser
coverage html
```

