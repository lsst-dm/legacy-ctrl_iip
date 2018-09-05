echo "Creating workdir"
mkdir ~/workdir

# Install dependencies
yum install -y java-1.7.0-openjdk java-1.7.0-openjdk-devel cmake ncurses-devel
yum groupinstall -y "Development Tools" 

# Install Rabbitmq-Server
## Install erlang 
echo "Installing Dependency::erlang..." 
cd ~/workdir
wget -O erlang-rpm.zip https://github.com/rabbitmq/erlang-rpm/archive/v20.3.0.zip
unzip erlang-rpm.zip
cd erlang-rpm-20.3.0
make 
cd RPMS/x86_64
yum install -y erlang-20.3-1.el7.centos.x86_64.rpm
cd ~/workdir

#### Install rabbitmq-server 
echo "Installing Rabbitmq-server..." 
cd ~/workdir
wget https://dl.bintray.com/rabbitmq/all/rabbitmq-server/3.7.4/rabbitmq-server-3.7.4-1.el7.noarch.rpm
rpm --import https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc
yum install rabbitmq-server-3.7.4-1.el7.noarch.rpm

### Install BOOST
echo "Installing boost..." 
yum install boost-devel

### Install Rabbitmq-r 
echo "Installing rabbitmq-c..." 
cd ~/workdir
wget -O rabbitmq-c.zip https://github.com/alanxz/rabbitmq-c/archive/v0.8.0.zip
unzip rabbitmq-c.zip
cd rabbitmq-c-0.8.0
mkdir build && cd build 
cmake .. 
cmake --build . --target install

### Install SimpleAmqpClient
echo "Installing SimpleAmqpClient..." 
cd ~/workdir
wget -O SimpleAmqpClient.zip https://github.com/alanxz/SimpleAmqpClient/archive/v2.4.0.zip
unzip SimpleAmqpClient.zip
cd SimpleAmqpClient-2.4.0
mkdir build && cd build
cmake ..
cmake --build . --target install

### Install Yaml-cpp
echo "Installing Yaml-cpp..." 
cd ~/workdir
wget -O yaml-cpp.zip https://github.com/jbeder/yaml-cpp/archive/yaml-cpp-0.5.3.zip
unzip yaml-cpp.zip 
cd yaml-cpp-yaml-cpp-0.5.3
mkdir build && cd build
cmake ..
cmake --build . --target install

echo "Installation Complete." 
