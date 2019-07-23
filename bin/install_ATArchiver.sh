DOWNLOAD_DIR=~/downloads
CTRL_IIP_PREFIX=/home/ATS/src/git 

yum update -y && yum install -y cmake make gcc-c++ openssl openssl-devel librabbitmq-0.8.0 librabbitmq-devel-0.8.0
useradd ATS
useradd redis

# Make directories
mkdir -p $DOWNLOAD_DIR $CTRL_IIP_PREFIX /var/log/iip

# Checkout ctrl_iip
cd $DOWNLOAD_DIR
curl -L https://github.com/lsst/ctrl_iip/archive/v2.1.tar.gz -o v2.1.tar.gz
tar zxvf v2.1.tar.gz
mv ctrl_iip-2.1 $CTRL_IIP_PREFIX/ctrl_iip

# Install C++ dependency libraries
# download boost 1.66
cd $DOWNLOAD_DIR
curl -L https://dl.bintray.com/boostorg/release/1.66.0/source/boost_1_66_0.tar.gz -o boost_1_66_0.tar.gz
tar zxvf boost_1_66_0.tar.gz
cd boost_1_66_0
./bootstrap.sh
./b2 install

# download yaml-cpp
cd $DOWNLOAD_DIR
curl -L https://github.com/jbeder/yaml-cpp/archive/yaml-cpp-0.5.3.tar.gz -o yaml-cpp-0.5.3.tar.gz
tar zxvf yaml-cpp-0.5.3.tar.gz
cd yaml-cpp-yaml-cpp-0.5.3/
mkdir build && cd build
cmake ..
cmake --build . --target install

# download SimpleAmqpClient
cd $DOWNLOAD_DIR
curl -L https://github.com/alanxz/SimpleAmqpClient/archive/v2.4.0.tar.gz -o v2.4.0.tar.gz
tar zxvf v2.4.0.tar.gz
cd SimpleAmqpClient-2.4.0/
mkdir build && cd build
cmake ..
cmake --build . --target install

# download cfitsio
cd $DOWNLOAD_DIR
curl -L http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio3450.tar.gz -o cfitsio3450.tar.gz
tar zxvf cfitsio3450.tar.gz
cd cfitsio/
mkdir build && cd build
cmake ..
cmake --build . --target install

chown -R ATS:ATS /home/ATS 
chown -R ATS:ATS /var/log/iip

# Install rabbitmq
curl -s https://packagecloud.io/install/repositories/rabbitmq/erlang/script.rpm.sh | bash
yum install -y erlang
rpm --import https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey
rpm --import https://packagecloud.io/gpg.key
curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.rpm.sh | bash
curl -L https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.7.16/rabbitmq-server-3.7.16-1.el7.noarch.rpm -o rabbitmq-server-3.7.16-1.el7.noarch.rpm
yum install -y rabbitmq-server-3.7.16-1.el7.noarch.rpm

# Install redis
curl -L http://download.redis.io/releases/redis-5.0.5.tar.gz -o redis-5.0.5.tar.gz
tar zxvf redis-5.0.5.tar.gz
cd redis-5.0.5
make
make install
touch /var/log/redis_6379.log
mkdir -p /var/lib/redis
chown -R redis:redis /var/log/redis_6379.log
chown -R redis:redis /var/lib/redis

# Copy systemd unit files
cp $CTRL_IIP_PREFIX/ctrl_iip/etc/services/* /etc/systemd/system/
systemctl enable l1d-ctrl_iip.target
