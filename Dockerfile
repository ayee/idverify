# Dockerfile used to build container based on SimpleCV
# and then append other packages to enable Django
#FROM sightmachine/simplecv
FROM ubuntu:16.04

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
#RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py -O - | python
RUN apt-get install -y python-pip

# SimpleCV Specific
RUN apt-get install -y libopencv-*
RUN apt-get install -y python-opencv
RUN apt-get install -y python-numpy
RUN apt-get install -y python-scipy
RUN apt-get install -y python-pygame
#RUN pip install PIL
RUN pip install ipython
RUN pip install pyzmq
RUN pip install jinja2
RUN pip install tornado
RUN pip install svgwrite

# SimpleCV Install
RUN wget https://github.com/sightmachine/SimpleCV/archive/master.zip
RUN unzip master
RUN cd SimpleCV-master; pip install -r requirements.txt; python setup.py install


RUN pip install Django==1.7.2
RUN apt-get update
RUN apt-get install -y python-yaml
RUN pip install PyYAML
RUN pip install cognitive-face
RUN pip install django-rest-swagger==0.2.8
RUN pip install djangorestframework==3.0.3
RUN pip install requests
RUN pip install pillow==2.7.0
RUN pip install python-status
RUN pip install argparse

# tesserocr install - tesserocr is
RUN pip install cython
RUN apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev
RUN pip install tesserocr

ADD . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]