import logging

import cv2
from SimpleCV import *

import detect_card
from card.base import BaseCard

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class driver_license(BaseCard):
    def __init__(self, args):
        self.card_aspect = 0.6305637982
        self.feature_angle = 93.1681203756
        self.name = 'California driving license'
        self.data_directory = 'data/gov/ca/driver_license'
        self.dn = 'gov.ca.driver_license'
        self.unique_id = 'gov.ca.driver_license'
        self.template_match_threshold = 2.5
        super(driver_license, self).__init__(args)


    def match(self, image):

        logging.info("Match image to template")
        simple_template, simple_warped = self.warp(image)
        simple_warped.getPIL().show()
        simple_template.getPIL().show()
        res = simple_warped.findTemplate(template_image=simple_template, threshold=self.template_match_threshold)

        if res and res[0].x == 0 and res[0].y == 0:
            logging.info("Template matched")
            # width = template.width
            # height = template.width * self.card_aspect
            # card = input_image.crop(x=res.x()[0], y=res.y()[0], w=width+10, h=height+10)
            # card = card.resize(w=1000)
            #
            # card = self.fix_rotation_twofeatures(card, 'top_left.png', ('top_right.png', 1, 'CCORR_NORM'))
            return self.parse(simple_warped)
        else:
            logging.info("Template not matched: %s", res)
            return None

    def warp(self, simple_image):
        '''
        Warp with OpenCV's approxPolyDP to approximate a polygonal curve(s) with the specified precision,
        and resize image to matching width of template
        :param image: SimpleCV image
        :return:
        '''

        # Convert SimpleCV image to opencv image
        image = simple_image.getNumpyCv2()
        # logging.info('Converted SimpleCV image %s to OpenCV images %s', simple_image, image)

        BINARY_THRESHOLD = 150
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE);
        area = [cv2.contourArea(cnt) for cnt in contours]
        card_contour = contours[area.index(max(area))]
        # Get approximate polygon
        pts = np.array(
                [p[0] for p in cv2.approxPolyDP(card_contour, 0.00001 * cv2.arcLength(card_contour, True), True)])
        # Apply four point transform to obtain a "birds eye view" of the image
        warped = detect_card.four_point_transform(image, pts)
        logging.info('Warped image shape = %s', warped.shape)
        height, width, channels = warped.shape

        if self.debug:
            cv2.imshow('Warped', cv2.resize(warped, (0, 0), fx=1, fy=1))
            cv2.waitKey(0)

        template = cv2.imread(self.data_directory + "/template.jpg")
        logging.info(u'Template shape = %s', template.shape)
        logging.info(u'Resizing to template\'s width %s by factor %s', template.shape[1], float(template.shape[1]) / width)
        # scale the warped image to match template
        resized_warped = cv2.resize(warped, (0, 0), fx=float(template.shape[1]) / width,
                            fy=float(template.shape[1]) * self.card_aspect / height, interpolation=cv2.INTER_CUBIC)
        logging.info(u'Warped image resized to {0:s}'.format(resized_warped.shape))

        simple_resized_warped = Image(resized_warped.transpose(1, 0, 2)[:, :, ::-1])
        simple_template = Image(template.transpose(1, 0, 2)[:, :, ::-1])
        return simple_template, simple_resized_warped

    def parse(self, card):
        self.get_text(card, "surname", x=385, y=246, w=280, h=36)
        self.get_text(card, "first_name", x=390, y=286, w=386, h=33)
        self.get_text(card, "birth_date", x=822, y=411, w=168, h=40)
        self.get_text(card, "birth_place", x=500, y=210, w=400, h=32)
        self.get_text(card, "date_of_issue", x=320, y=260, w=170, h=32)
        self.get_text(card, "date_of_expiry", x=580, y=260, w=170, h=32)
        self.get_text(card, "street_address", x=331, y=309, w=600, h=36)
        self.get_text(card, 'city_state_zip', x=336, y=346, w=600, h=36)
        self.get_text(card, "card_no", x=385, y=123, w=227, h=48)
        self.get_text(card, "categories", x=580, y=400, w=300, h=32)

        self.unique_id += self.fields['card_no']

        self.get_signature(card, x=320, y=388, w=217, h=87)
        license_photo = self.get_photo(card, x=26, y=123, w=296, h=395)
        import cognitive_face as CF
        KEY = '558b0e3d935741d3a76578dc0e1e4e81'  # Replace with a valid Subscription Key here.
        CF.Key.set(KEY)
        license_photo.save("debug/test.jpg")
        license = CF.face.detect("debug/test.jpg")[0]
        selfie = CF.face.detect('/Users/ayee/git/cardscan/data/gov/ca/IMG_6942.JPG')[0]
        print CF.face.verify(license['faceId'], selfie['faceId'])

        structure = {
            'card': {
                'type': 'gov.ca.driver_license',
                'class': 'driving-license'
            },
            'country': 'us',
            'licenceId': self.fields['card_no'],
            'person': {
                'surname': self.fields['surname'],
                'firstname': self.fields['first_name'],
                'birth': {
                    'date': self.parse_date(self.fields['birth_date']),
                    'place': self.fields['birth_place']
                },
            },
            'validity': {
                'start': self.parse_date(self.fields['date_of_issue']),
                'end': self.parse_date(self.fields['date_of_expiry'])
            },
            'street_address': self.fields['street_address'],
            'city_state_zip': self.fields['city_state_zip'],
            'categories': self.parse_categories(self.fields['categories'])
        }

        if self.debug:
            card.save("debug/" + self.dn + "_gettext.png")

        return structure

    def parse_date(self, datestr):
        # datestr: 12.12.1900
        datestr = datestr.replace(" ", "").replace(".", "")  # remove space and dot because they are common OCR mistakes
        try:
            month = datestr[0:2]
            day = datestr[2:4]
            year = datestr[4:8]
            datestr = "{}-{}-{}".format(year, month, day)  # 1900-12-12
        except:
            return "invalid"
        return datestr

    def parse_categories(self, categorystr):
        # categorystr: AM-B
        categorystr = categorystr.replace(" ", "").lower()
        categories = categorystr.split("-")
        result = {
            'moped': 'am' in categories,
            'bike11kw': 'a1' in categories,
            'bike35kw': 'a2' in categories,
            'bike': 'a' in categories,
            'car': 'b' in categories,
            'truck': 'c' in categories,
            'lightTruck': 'c1' in categories,
            'lightTruckWithTrailer': 'c1e' in categories,
            'bus': 'd' in categories,
            'smallBus': 'd1' in categories,
            'carWithTraler': 'be' in categories,
            'truckWithTrailer': 'ce' in categories,
            'busWithTrailer': 'de' in categories,
            'smallBusWithTrailer': 'd1e' in categories,
            'tractor': 't' in categories
        }
        return result