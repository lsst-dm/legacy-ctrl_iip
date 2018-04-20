mkdir /etc/redis
mkdir /var/redis

cp redis_init_script /etc/init.d/redis_6379
cp redis.conf /etc/redis/6379.conf

mkdir /var/redis/6379
# update-rc.d redis_6379 defaults # Add redis-server to every run level
