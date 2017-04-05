idverify
========

Django/Python based web application and API to parse scanned photo identification documents with cards to various data structures

features:
 - Reads cards from any valid image source for [SimpleCV][simplecv] (Currently expects 300 dpi images)
 - Outputs a yaml or json data structure
 - Reads multiple cards from a single image (Multiple cards on the scanbed)
 
Supported cards:
 - CA driver license
 - Dutch personal indentification card
 - Dutch driving licence
 
## Development
Project is [dockerized](https://github.com/ayee/idverify/blob/master/Dockerfile)
Follow these steps to start development 

1. Install [Docker Toolbox for Mac])https://docs.docker.com/toolbox/toolbox_install_mac/). Note that there's a [difference](https://docs.docker.com/docker-for-mac/docker-toolbox/#setting-up-to-run-docker-for-mac) between Docker Toolbox and Docker for Mac.  Reason to use Toolbox is AWS ElasticBean and its documentation assumes Docker Toolbox

2. Once installed, should be able to type `Docker Quickstart Terminal` in Spotlight Search and start Docker environment.

3. In order to build a image from Dockerfile in this project, run
    ```bash
    docker build -t idverify .
    ```
    A docker image is built with the name 'idverfiy' and can be verified with:
    ```bash
    docker images
    ```
4. With PyCharm as IDE, create a Remote Python Interpreter with created image
5. All Run and Debug should be run with the docker remote interpreter

## Deployment

Deployment is done using AWS ElasticBeanstalk 
1. Create [Elastic Beanstalk single container docker](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker.html) environment using `eb init`.  Note that it requires [EB CLI version 3.3 or greater](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html)
2. Once that's done, should be able to run the app locally with ElasticBean and Docker
    ```
    eb local run
    ```
    The website should be avaible to the http://192.168.99.100:8000/api/docs/
    
3. 

## Installation

cardscan depends on `python2.7`, `SimpleCV`, `pyyaml`, `tesseract-ocr` and `python-tesseract`

```bash
$ sudo apt-get install python2 tesseract-ocr
# simplecv instructions
$ sudo apt-get install ipython python-opencv python-scipy python-numpy python-pygame python-setuptools python-pip
$ sudo pip install https://github.com/sightmachine/SimpleCV/zipball/develop
# python-tesseract installation
$ wget "https://bitbucket.org/3togo/python-tesseract/downloads/python-tesseract_0.9-0.3ubuntu0_amd64.deb"
$ sudo dpkg -i python-tesseract_0.9-0.3ubuntu0_amd64.deb
$ sudo apt-get -f install
# pyyaml installation
$ sudo pip install pyyaml
# cardscan installation
$ git clone git@github.com:MartijnBraam/cardscan.git
$ cd cardscan
$ echo ":)"
```

## Example output

This is censored example output from a scan of a dutch indentification card
```yaml
- card:
    class: personal-indentification
    type: nl.government.idcard
  authority: Burg. van Midden-Drenthe
  country: nl
  documentId: ********
  person:
    birth: {date: '1900-01-01', place: Amsterdam}
    gender: male
    givenNames: Example First Names
    height: 1.92
    nationality: Nederlandse
    personalId: ********
    surname: Example-Lastname
  validity: 
    start: 2012-1-09
    end: 2017-1-09
```

 
  [simplecv]: http://simplecv.org/
