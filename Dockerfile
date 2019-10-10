FROM centos:7
WORKDIR /app
COPY . /app
RUN yum update -y && \
    yum install -y \
        epel-release \
        gcc-c++-4.8.5 \
        rpm-build \
        make \
        cmake-2.8.12.2 \
        cmake3-3.14.6 \
        which-2.20 \
        librabbitmq-0.8.0 \
        librabbitmq-devel-0.8.0 \
        libcurl-7.29.0 \
        libcurl-devel-7.29.0
#RUN mkdir build && \
#    cd build && \
#    cmake3 .. && \
#    cmake3 --build .

# Cannot use boost169 coz unit_test_framework is not provided
# boost169
