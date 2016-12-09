from SimpleCV import *
from card.base import BaseCard
from time import strptime
import detect_card
import cv2
import logging

class drivinglicence(BaseCard):
    def __init__(self, args):
        self.card_aspect = 0.6305637982
        self.feature_angle = 93.1681203756
        self.name = 'California driving license'
        self.data_directory = 'data/gov/ca/dmv'
        self.dn = 'gov.ca.dmv'
        self.unique_id = 'gov.ca.dmv'
        self.template_match_threshold = 2.5
        super(drivinglicence, self).__init__(args)


    def match(self, image):

        # Convert SimpleCV image to opencv image
        image = image.getNumpy()

        template, warped = self.warp(image)

        logging.info("Match image to template ... ")

        # Convert opencv warped image back to SimpleCV.ImageClass
        simple_warped = Image(warped)
        template = Image(template)

        res = simple_warped.findTemplate(template_image=template, threshold=self.template_match_threshold)
        ## Use opencv to match template
        # res = cv2.matchTemplate(warped, template, cv2.TM_CCOEFF)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print min_val, max_val, min_loc, max_loc
        # h = template.shape[0]
        # w = template.shape[1]
        # top_left = max_loc
        # bottom_right = (top_left[0] + w, top_left[1] + h)
        # print top_left, bottom_right

        if res:
            # width = template.width
            # height = template.width * self.card_aspect
            # card = input_image.crop(x=res.x()[0], y=res.y()[0], w=width+10, h=height+10)
            # card = card.resize(w=1000)
            #
            # card = self.fix_rotation_twofeatures(card, 'top_left.png', ('top_right.png', 1, 'CCORR_NORM'))
            return self.parse(simple_warped)
        else:
            return None

    def warp(self, image):
        BINARY_THRESHOLD = 150
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE);
        area = [cv2.contourArea(cnt) for cnt in contours]
        card_contour = contours[area.index(max(area))]
        # Get approximate polygon
        pts = np.array(
                [p[0] for p in cv2.approxPolyDP(card_contour, 0.00001 * cv2.arcLength(card_contour, True), True)])
        # apply the four point tranform to obtain a "birds eye view" of the image
        warped = detect_card.four_point_transform(image, pts)
        print warped.shape
        height, width, channels = warped.shape
        template = cv2.imread(self.data_directory + "/template.jpg")
        print template.shape
        print float(template.shape[1]) / width
        print float(template.shape[1]) * 0.6305637982 / height
        # scale the warped image to match template
        warped = cv2.resize(warped, (0, 0), fx=float(template.shape[1]) / width,
                            fy=float(template.shape[1]) * 0.6305637982 / height, interpolation=cv2.INTER_CUBIC)
        return template, warped

    def parse(self, card):
        self.get_text(card, "surname", x=385, y=389, w=368, h=36)
        self.get_text(card, "first_name", x=320, y=166, w=600, h=32)
        self.get_text(card, "birth_date", x=320, y=210, w=170, h=32)
        self.get_text(card, "birth_place", x=500, y=210, w=400, h=32)
        self.get_text(card, "date_of_issue", x=320, y=260, w=170, h=32)
        self.get_text(card, "date_of_expiry", x=580, y=260, w=170, h=32)
        self.get_text(card, "authority", x=320, y=310, w=600, h=32)
        self.get_text(card, "card_no", x=320, y=357, w=210, h=32)
        self.get_text(card, "categories", x=580, y=400, w=300, h=32)

        self.unique_id += self.fields['card_no']

        self.get_signature(card, x=320, y=388, w=217, h=87)
        self.get_photo(card, x=60, y=150, w=217, h=320)

        structure = {
            'card': {
                'type': 'nl.government.drivinglicence',
                'class': 'driving-licence'
            },
            'country': 'nl',
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
            'authority': self.fields['authority'],
            'categories': self.parse_categories(self.fields['categories'])
        }

        if self.debug:
            card.save("debug/" + self.dn + "_gettext.png")

        return structure

    def parse_date(self, datestr):
        # datestr: 12.12.1900
        datestr = datestr.replace(" ", "").replace(".", "")  # remove space and dot because they are common OCR mistakes
        try:
            day = datestr[0:2]
            month = datestr[2:4]
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