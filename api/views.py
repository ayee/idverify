from django.shortcuts import render
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
import cognitive_face as CF
import uuid

from cardScan import CardScan

KEY = '558b0e3d935741d3a76578dc0e1e4e81'  # Replace with a valid Subscription Key here.
CF.Key.set(KEY)

@api_view(['POST'])
@parser_classes((FileUploadParser,))
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def upload_card(request):
    '''
    Upload card image and start verification session
    :param request:
    :return:
    '''

    # Create new verification session
    session_id = 'test' # uuid.uuid4()
    # TODO: save received card image to s3
    with open('debug/' + str(session_id) + '_card_img.jpg','w') as f:
        f.write(request.stream.read())
    print CF.face.detect('debug/' + str(session_id) + '_card_img.jpg')[0]

    return Response('received card')


@api_view(['POST'])
@parser_classes((FileUploadParser,))
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
def upload_portrait_and_verify(request):

    # TODO: save received card image to s3
    session_id = 'test' # uuid.uuid4()
    with open('debug/' + str(session_id) + '_portrait_img.jpg','w') as f:
        f.write(request.stream.read())

    import argparse
    parser = argparse.ArgumentParser(description='Tool to extract json objects from scanned cards')
    parser.add_argument('filename', help="File to scan for cards. This tool currently expects it to be 300dpi")
    parser.add_argument('picture', help='File of picture to verify against picture in identification card')
    parser.add_argument('-v', '--verbose', action="store_true", help="Enable verbose output")
    parser.add_argument('-f', '--format', help="Output formatting", choices=['json', 'yaml'], default="yaml")
    parser.add_argument('-d', '--debug',
                        help="This creates a debug directory in the current directory with debug files from the card classes",
                        action="store_true")
    parser.add_argument('-e', '--export', help="Export extracted images like signature and photo", action="store_true")
    args = parser.parse_args()
    cardscan = CardScan(args)
    cardscan.parse('debug/' + str(session_id) + '_card_img.jpg', 'debug/' + str(session_id) + '_portrait_img.jpg')
    # print CF.face.detect('debug/' + str(session_id) + '_card_img.jpg')[0]
    # print CF.face.detect(request.stream)[0]

    return Response('Verified')