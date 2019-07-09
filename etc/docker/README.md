# Description

## Dockerfiles
### Prerequisites
* Must be in the $CTRL_IIP_DIR

### Commands
```{bash}
$ docker build -t iip-development:test -f ./etc/docker/development-Dockerfile .
$ docker run -it \
> --mount type=bind,src=$(pwd),target=/app \
> iip-development:test bash
```

## Docker-compose
### Prerequisites
1. Setup environment variables
* Edit ./etc/config/rmq_cfg.env.template file with already created rabbitmq 
username, password and vhost
* Rename the rmq_cfg.env.template file to rmq_cfg.env(meaning you don't
actually check in username and password for RabbitMQ server)

2. Setup rabbitmq credentials 
Inside rabbitmq container, 
* Add RabbitMQ user, password and vhost 
* Set permissions for user in vhost given
<or>
`$ bash ${CTRL_IIP_DIR}/bin/rmq_init.sh`

3. In the directory that docker-compose is gonna run, create `.env` file 
from `$CTRL_IIP_DIR/etc/config/docker_env.template` and set the values.

### Commands
```{bash} 
$ docker-compose build 
$ docker-compose up 
$ docker-compose down
```
