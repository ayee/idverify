from SimpleCV import Image
from django.test import TestCase
from driver_license import driver_license

class DriverLicenseTestCase(TestCase):
    def setUp(self):
        self.driver_license = driver_license({'debug': False})

    def test_warp(self):
        unwarped = Image('data/test_local/california-driving-license-front4.jpg')
        self.assertEqual(unwarped.width, 1010)
        self.assertEqual(unwarped.height, 637)
        template, warped = self.driver_license.warp(unwarped)
        warped.save("data/test_local/test_warped.jpg")








