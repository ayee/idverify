from SimpleCV import *
import math
import tesserocr

class BaseCard(object):
    def __init__(self, args):
        self.fields = {}
        self.card = None
        self.args = args
        self.debug = args['debug']
        self.export = args['export']

    def get_text(self, card, label, x, y, w, h, color=Color.BLACK, binarize=True):
        """
        Parse text using tesseract-ocr via python wrapper tesserocr
        :param binarize:
        :param card:
        :param label:
        :param x:
        :param y:
        :param w:
        :param h:
        :param color:
        :param binarize: Binarize before OCR.  Default is True
        :return:
        """
        field = card.crop(x=int(x), y=int(y), w=int(w), h=int(h))
        if binarize:
            field = field.whiteBalance().grayscale().binarize()  # Convert to grayscale and increase brightness
        try:
            # field_text = field.readText().strip().split("\n")[0] # Run tesseract OCR and cleanup result
            field_text = tesserocr.image_to_text(field.getPIL()).strip().split("\n")[0] # Use an alternative Tesseract OCR python package
        except:
            field_text = ""

        if self.debug:
            if not os.path.isdir("debug/get_text"):
                os.mkdir("debug/get_text")
            field.save("debug/get_text/" + label + ".png")
            # card.drawRectangle(x=x, y=y, w=w, h=h, color=Color.RED)
            # card.drawText("{}: {}".format(label, field_text), x=x+10, y=y, color=Color.RED)
            card.save('debug/get_text/get_text_card.png')
        self.fields[label] = field_text
        return field_text

    def get_signature(self, card, x, y, w, h):
        field = card.crop(x=x, y=y, w=w, h=h)
        field = field.grayscale().binarize().invert()
        if self.debug:
            card.drawRectangle(x=x, y=y, w=w, h=h, color=Color.RED)
            card.drawText("Signature", x=x+10, y=y, color=Color.RED)
        if self.export:
            field.save(self.unique_id + ".signature.png")

    def get_photo(self, card, x, y, w, h):
        field = card.crop(x=x, y=y, w=w, h=h)
        if self.debug:
            card.drawRectangle(x=x, y=y, w=w, h=h, color=Color.RED)
            card.drawText("Photo", x=x+10, y=y, color=Color.RED)
        if self.export:
            field.save(self.unique_id + ".photo.png")
        return field

    def get_feature_center(self, card, filename):
        if isinstance(filename, str):
            feature_template = Image(self.data_directory + "/" + filename)
            feature_match = card.findTemplate(template_image=feature_template, threshold=5)
        elif len(filename) == 2:
            feature_template = Image(self.data_directory + "/" + filename[0])
            feature_match = card.findTemplate(template_image=feature_template, threshold=filename[1])
        else:
            feature_template = Image(self.data_directory + "/" + filename[0])
            feature_match = card.findTemplate(template_image=feature_template, threshold=filename[1], method=filename[2])

        if self.debug:
            feature_match.draw(color=Color.LIME)
        feature_bounds = feature_match[0].boundingBox()
        feature_center = (feature_bounds[0]+feature_bounds[2]/2, feature_bounds[1]+feature_bounds[3]/2)
        return feature_center

    def fix_rotation_twofeatures(self, card, feature1, feature2):
        feature1_center = self.get_feature_center(card, feature1)
        feature2_center = self.get_feature_center(card, feature2)

        if self.debug:
            card.drawPoints([feature1_center, feature2_center], color=Color.LIME)
            card.drawLine(feature1_center, feature2_center, color=Color.LIME)
            card.save("debug/" + self.dn + "_fix_rotation.png")

        dx, dy = feature2_center[0]-feature1_center[0], feature2_center[1]-feature1_center[1]
        rads = math.atan2(dx, dy)
        degrees = math.degrees(rads)
        delta_angle = degrees - self.feature_angle
        if self.debug:
            print("Rotation correction: {} degrees (expect: {}, found: {})".format(delta_angle, self.feature_angle, degrees))
        card = card.rotate(delta_angle)
        if self.debug:
            card.save("debug/" + self.dn + "_fix_rotation_corrected.png")
        return card
