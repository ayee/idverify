from SimpleCV import Image
from django.test import TestCase
from driver_license import driver_license
import tesserocr

class DriverLicenseTestCase(TestCase):

    def crop_field_images(self):
        # crops field images used for ocr testing
        self.ocr_ = 'data/test_local/ocr/'
        self.license_image = 'data/test_local/california-driving-license-front4.jpg'
        unwarped = Image(self.license_image)
        template, warped = self.driver_license.warp(unwarped)
        warped.crop(x=395, y=104, w=227, h=48).save('%license_number.jpg')
        warped.crop(x=385, y=234, w=280, h=36).save('%slastname.jpg' % self.ocr_)
        warped.crop(x=390, y=272, w=420, h=33).save('%sfirstname.jpg' % self.ocr_)
        warped.crop(x=822, y=411, w=168, h=40).save('%sbirthdate.jpg' % self.ocr_)
        warped.crop(x=416, y=369, w=200, h=50).save('%sbirthdate_red.jpg' % self.ocr_)
        warped.crop(x=834, y=580, w=170, h=32).save('%sissuedate.jpg' % self.ocr_)
        warped.crop(x=408, y=190, w=210, h=40).save('%sexpirydate.jpg' % self.ocr_)
        warped.crop(x=331, y=309, w=600, h=36).save('%sstreetaddress.jpg' % self.ocr_)
        warped.crop(x=336, y=329, w=600, h=36).save('%scitystatezip.jpg' % self.ocr_)

    def setUp(self):
        self.driver_license = driver_license({'debug': True, 'export': True})
        self.crop_field_images()

    def test_warp(self):
        """
        Test perspective correction
        :return:
        """
        unwarped = Image('data/test_local/california-driving-license-front4.jpg')
        template, warped = self.driver_license.warp(unwarped)
        warped.save("data/test_local/test_warped.jpg")
        self.assertEqual(warped.width, 1010)
        self.assertEqual(warped.height, 637)

    def test_match_template(self):
        unwarped = Image('data/test_local/california-driving-license-front4.jpg')
        # unwarped = Image('data/test_local/IMG_5795.JPG')
        # unwarped = Image('data/test_local/IMG_5711.JPG')
        template, warped = self.driver_license.warp(unwarped)
        self.assertEqual(template.height, 120)
        self.assertEqual(template.width, 1010)
        match = warped.findTemplate(template_image=template, threshold=1.5)
        warped.save('data/test_local/test_match_template1.jpg')
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0].x, 0)
        self.assertEqual(match[0].y, 0)

    def test_parse_driver_license(self):
        # unwarped =
        template, license = self.driver_license.warp(Image('data/test_local/new-dl-2012-1.jpg'))
        selfie = 'data/test_local/brad-pitt-face.jpg'
        '''
        {'city_state_zip': u'SACRAMENTO, CA 95818',
                          'country': 'us',
                          'validity':
                              {'start': u'08/31/2009}',
                               'end': '2014-08-31'},
                          'person': {
                              'lastname': u'SAMPLE',
                              'birthdate': '1977-03-31',
                              'firstname': u'ALEXANDER J.'},
                          'card': {
                              'type': 'gov.ca.driver_license',
                              'class': 'driving-license'},
                          'license_number': u'l1 234562',
                          'street_address': u'2570 24TH STREET'}
        '''
        fields = self.driver_license.parse(license, selfie)
        self.assertEqual(fields['city_state_zip'], u'SACRAMENTO, CA 95818')
        self.assertEqual(fields['validity']['start'], '08/31/2009)')
        self.assertEqual(fields['validity']['end'], '2014-08-31')
        self.assertEqual(fields['person']['lastname'], 'SAMPLE')

        # TODO: Slight position differences breaks OCR, use templates to find field header images and then offset to capture text
        # template, license = self.driver_license.warp(Image('data/test_local/IMG_5795.JPG'))
        # license.save('data/test_local/IMG_5795_WARPED.JPG')
        # self.assertEqual(self.driver_license.parse(license, selfie), '')


    def test_ocr_license_number(self):
        unwarped = Image('data/test_local/new-dl-2012-1.jpg')
        template, warped = self.driver_license.warp(unwarped)
        # warped.save('data/test_local/warped.jpg')
        field = warped.crop(x=395, y=118, w=227, h=48)
        binarized = field.whiteBalance().grayscale().binarize()
        binarized.save('data/test_local/test_ocr_license_number_binarized.jpg')
        license_number = tesserocr.image_to_text(binarized.getPIL()).strip().split("\n")[0]
        self.assertEqual(license_number, u'l1 2345623')
        field.save('data/test_local/test_ocr_license_number/license_number.jpg')
        license_number = tesserocr.image_to_text(field.getPIL()).strip().split("\n")[0]
        self.assertEqual(license_number, u'I1 234562')

    def test_ocr(self):
        self.ocr_dir = 'data/test_local/ocr/'
        self.assertEqual(tesserocr.image_to_text(
            Image('%slastname.jpg' % self.ocr_dir).getPIL()), "COLLIER\n\n")
        self.assertEqual(tesserocr.image_to_text(
            Image('%sfirstname.jpg' % self.ocr_dir).getPIL()), "ROBERT HUTCHESON III\n\n")
        self.assertEqual(tesserocr.image_to_text(
            Image('%scitystatezip.jpg' % self.ocr_dir).getPIL()), u'BOULDER CREEK. CA 95006\n\n')
        # binarize() produces better result
        self.assertEqual(tesserocr.image_to_text(
            Image('%sbirthdate_red.jpg' % self.ocr_dir).getPIL()), u'09/18/1950\n\n')
        self.assertEqual(tesserocr.image_to_text(
            Image('%sissuedate.jpg' % self.ocr_dir).getPIL()), u'\u201c18/05/2014\n\n')
        self.assertEqual(tesserocr.image_to_text(
            Image('%sbirthdate.jpg' % self.ocr_dir).getPIL()), u'00181960\n\n') # WRONG
        self.assertEqual(tesserocr.image_to_text(
            Image("%sissuedate_02.png" % self.ocr_dir).getPIL()), u'08/31/2009 }\n\n')


    def test_ocr_binarized(self):
        self.ocr_dir = 'data/test_local/ocr/'
        self.assertEqual(tesserocr.image_to_text(
            Image('%slicense_number.jpg' % self.ocr_dir).binarize().getPIL()), '30256042\n\n')
        self.assertEqual(tesserocr.image_to_text(
            Image('%slastname.jpg' % self.ocr_dir).binarize().getPIL()), "COLLIER\n\n")
        self.assertEqual(tesserocr.image_to_text(
            Image('%sfirstname.jpg' % self.ocr_dir).binarize().getPIL()), "ROBERT HUTCHESON Ill\n\n") # Wrong
        self.assertEqual(tesserocr.image_to_text(
            Image('%scitystatezip.jpg' % self.ocr_dir).binarize().getPIL()), u'\xe9bULD\xe9R \xe9\ufb01r\ufb01ex\u2019, CA 95005\n\n')
        self.assertEqual(tesserocr.image_to_text(
            Image('%sbirthdate_red.jpg' % self.ocr_dir).binarize().getPIL()), u'09/18/1950\n\n')
        self.assertEqual(tesserocr.image_to_text(
            Image('%sissuedate.jpg' % self.ocr_dir).binarize().getPIL()), "08/05/2014\n\n")
        self.assertEqual(tesserocr.image_to_text(
            Image('%sbirthdate.jpg' % self.ocr_dir).binarize().getPIL()), u'09181960\n\n') # Still wrong by one digit, correct date is 09181950
        self.assertEqual(tesserocr.image_to_text(
            Image('%sexpirydate.jpg' % self.ocr_dir).binarize().getPIL()), u'09/18/2019\n\n')


    def test_get_text(self):
        template, card = self.driver_license.warp(Image('data/test_local/california-driving-license-front4.jpg'))
        card.save('data/test_local/warped.jpg')
        self.assertEqual(self.driver_license.get_text(card, "first_name", x=390, y=272, w=420, h=33), "ROBERT HUTCHESON Ill")
        self.assertEqual(self.driver_license.get_text(card, "first_name", x=390, y=272, w=420, h=33, binarize=False), "ROBERT HUTCHESON Ill")
        self.assertEqual(self.driver_license.get_text(card, "city_state_zip", x=336, y=329, w=600, h=36), u'\xe9bULD\xe9R \xe9\ufb01e\u2019ex\u2019, CA 95005')
        self.assertEqual(self.driver_license.get_text(card, "city_state_zip", x=336, y=329, w=600, h=36, binarize=False), u'BOULDER CREEK. CA 95006')
        self.assertEqual(self.driver_license.get_text(card, 'birthdate_red', x=416, y=369, w=200, h=50), u'09/18/1950')
        self.assertEqual(self.driver_license.get_text(card, 'birthdate_red', x=416, y=369, w=200, h=50, binarize=False), u'09/18/1950')
        self.assertEqual(self.driver_license.get_text(card, 'issue_date', x=834, y=580, w=170, h=32), '08/05/2014')
        self.assertEqual(self.driver_license.get_text(card, 'issue_date', x=834, y=580, w=170, h=32, binarize=False), u'108/05I2014')











