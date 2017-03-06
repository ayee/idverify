# Dockerfile used to build container based on SimpleCV
# and then append other packages to enable Django
FROM sightmachine/simplecv

RUN pip install Django==1.7.2
RUN apt-get update
RUN apt-get install -y python-yaml
RUN pip install PyYAML
RUN pip install cognitive-face
RUN pip install django-rest-swagger==0.2.8
RUN pip install djangorestframework==3.0.3
RUN pip install requests

ADD . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]