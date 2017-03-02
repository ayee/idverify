# Build with
# sudo docker -t="simplecv" .
# Run with
# sudo docker run -p 54717:8888 -t -i simplecv

FROM ubuntu:12.04

MAINTAINER Anthony Oliver <anthony@sightmachine.com>

# Install system dependencies
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y unzip
RUN apt-get install -y wget
RUN apt-get install -y clang
RUN apt-get install -y cmake
RUN apt-get install -y python2.7
RUN apt-get install -y python2.7-dev
RUN apt-get install -y python-setuptools
RUN wget https://bootstrap.pypa.io/get-pip.py -O - | python

# SimpleCV Specific
RUN apt-get install -y libopencv-*
RUN apt-get install -y python-opencv
RUN apt-get install -y python-numpy 
RUN apt-get install -y python-scipy
RUN apt-get install -y python-pygame
# RUN pip install PIL
RUN pip install ipython
RUN pip install pyzmq
RUN pip install jinja2
RUN pip install tornado
RUN pip install Django==1.7.2
RUN pip install PyYAML==3.11
RUN pip install cognitive-face==1.2.1
RUN pip install django-rest-swagger==0.2.8
RUN pip install djangorestframework==3.0.3
RUN pip install requests==2.13.0
RUN pip install scipy==0.13.2
RUN pip install wsgiref==0.1.2

# SimpleCV Install
RUN wget https://github.com/sightmachine/SimpleCV/archive/master.zip
RUN unzip master
RUN cd SimpleCV-master; pip install -r requirements.txt; python setup.py install

# Use clang
ENV CC clang
ENV CXX clang++

# Environment setup
EXPOSE 8000
