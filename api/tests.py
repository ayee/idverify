from PIL import Image
from django.test import TestCase
import tempfile
import status
from io import BytesIO
import views

# Create your tests here.

from rest_framework.test import APIRequestFactory
from django.test import TestCase

class RestApiTestCase(TestCase):

    # def setUp(self):
    #     self.client =

    # def test_that_authentication_is_required(self):
    #     self.assertEqual(self.client.post('my_url').status_code, status.HTTP_401_UNAUTHORIZED)

    def test_image_upload_request_body(self):
        factory = APIRequestFactory()
        request = factory.post('/api/upload_card', {'title': 'new idea'})

    def test_file_is_accepted(self):
        # self.client.force_authenticate(self.user)
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        response = self.client.post('/api/upload', {'card': tmp_file, 'selfie': tmp_file}, format='multipart')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    # def test_upload_card(self):
    #     '''
    #     curl -i -X POST 127.0.0.1:8000/api/upload_card -H "Content-Type: image/jpeg" --data-binary "@/Users/ayee/Downloads/IMG_5795.JPG"
    #     '''
    #     import requests
    #     response = self.client.post('/api/upload_card', data=file('data/test_local/brad-pitt-drivers-license.jpg', 'rb').read())
    #     self.assertEqual(status.HTTP_201_CREATED, response.status_code)


    def test_upload_multiple_images(self):
        '''
        Test upload multiple images at a time
        :return:
        '''
        # self.client.force_authenticate(self.user)
        brad_pitt_license = open('data/test_local/brad-pitt-drivers-license.jpg', 'rb')
        brad_pitt_face = open('data/test_local/brad-pitt-face.jpg', 'rb')
        data = {
            'card': brad_pitt_license,
            'selfie': brad_pitt_face
        }
        response = self.client.post('/api/upload', data, format='multipart')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)


    def test_verify_fake_id(self):
        fake_license = open('data/test_local/california-driving-license-front2.jpg', 'rb')
        brad_pitt_face = open('data/test_local/brad-pitt-face.jpg', 'rb')
        response = self.client.post('/api/verify_simple', {
            'card': fake_license,
            'selfie': brad_pitt_face
        }
        , format='multipart')
        # TODO Change output to better show unmatched
        self.assertEqual(response.content, '"[]"')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_verfiy_brad_pitt(self):
        '''
        Test simply verify (one call)
        :return:
        '''
        # self.client.force_authenticate(self.user)
        brad_pitt_license = open('data/test_local/brad-pitt-drivers-license.jpg', 'rb')
        brad_pitt_face = open('data/test_local/brad-pitt-face.jpg', 'rb')
        data = {
            'card': brad_pitt_license,
            'selfie': brad_pitt_face
        }
        response = self.client.post('/api/verify_simple', data, format='multipart')
        # TODO Change output to better show unmatched
        self.assertEqual(response.content, '"[]"')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_views_upload(self):
        '''
        Test with APIRequestFactory and views directly
        :return:
        '''
        # This is a 1x1 black png
        simple_png = BytesIO(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc````\x00\x00\x00\x05\x00\x01\xa5\xf6E@\x00\x00\x00\x00IEND\xaeB`\x82')
        simple_png.name = 'test.png'
        factory = APIRequestFactory()
        post = factory.post('/upload', data={'image': simple_png})
        views.upload(post)

    def test_echo(self):
        response = self.client.post('/api/echo/', {'msg': 'Can you hear me?'}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

