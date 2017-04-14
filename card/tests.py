from django.test import TestCase
import cognitive_face as CF

class MicrosoftCognitiveTestCase(TestCase):

    def test_detect_face(self):
        brad_pitt_license = CF.face.detect('data/test_local/brad-pitt-drivers-license.jpg')[0]
        brad_pitt_face = CF.face.detect('data/test_local/brad-pitt-face.jpg')[0]
        print CF.face.verify(brad_pitt_face['faceId'], brad_pitt_license['faceId'])

    @classmethod
    def setUpClass(cls):
        """
        set up key
        """
        super(MicrosoftCognitiveTestCase, cls).setUpClass()
        KEY = '558b0e3d935741d3a76578dc0e1e4e81'  # Replace with a valid Subscription Key here.
        CF.Key.set(KEY)


def old_function(self):

    KEY = '558b0e3d935741d3a76578dc0e1e4e81'  # Replace with a valid Subscription Key here.
    CF.Key.set(KEY)

    # Time (in seconds) for sleep between each call to avoid exceeding quota.
    # Default to 3 as free subscription have limit of 20 calls per minute.
    TIME_SLEEP = 3

    # result = CF.face.detect('https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg')
    # print result[0]['faceId']
    #
    # brad_pitt_license = CF.face.detect('http://cdn01.cdn.justjared.com/wp-content/uploads/headlines/2006/06/brad-pitt-drivers-license.jpg')[0]
    # brad_pitt_face = CF.face.detect('https://s-media-cache-ak0.pinimg.com/564x/59/46/48/594648cfa3f40ea28568ff550d3570b0.jpg')[0]
    # brad_pitt_face2 = CF.face.detect('https://cdn.pursuitist.com/wp-content/uploads/2012/05/Brad-Pitt-Named-The-New-Face-of-Chanel-N5.png')[0]
    # brad_pitt_face_slanted = CF.face.detect('https://theslanted.com/wp-content/uploads/2016/08/Allied.jpg')[0]
    # brad_pitt_face_rotated = CF.face.detect('http://1.bp.blogspot.com/_mJ4lc_Q9Q6k/RdIj9rvK_oI/AAAAAAAABEg/o2lDSU4xBAY/s400/brad_pitt.jpg')[0]
    # white_male_face = CF.face.detect('https://s-media-cache-ak0.pinimg.com/564x/03/46/fb/0346fb932e93942866df0d6e10fb6b1c.jpg')[0]
    #
    # print CF.face.verify(brad_pitt_face['faceId'], brad_pitt_license['faceId'])
    # print CF.face.verify(brad_pitt_license['faceId'], brad_pitt_face2['faceId'])
    # print CF.face.verify(brad_pitt_license['faceId'], brad_pitt_face_slanted['faceId'])
    # print CF.face.verify(brad_pitt_license['faceId'], brad_pitt_face_rotated['faceId'])
    # print CF.face.verify(brad_pitt_license['faceId'], white_male_face['faceId'])

    # Testing driver license pic and selfie
    my_license = CF.face.detect('data/test_local/IMG_5711.JPG')[0]
    # selfie = CF.face.detect('/Users/ayee/git/cardscan/data/gov/ca/IMG_6942.JPG')[0]
    # print CF.face.verify(my_license['faceId'], selfie['faceId'])

    # Test first loading pictures with SimpleCV and then use Cognitive Face
    from SimpleCV import *
    my_license = Image('/Users/ayee/Downloads/IMG_5711.JPG')
