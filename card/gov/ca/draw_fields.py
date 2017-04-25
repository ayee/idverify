import argparse
import sys
import yaml
from SimpleCV import Image, Color
import tesserocr


def main(argv):
    conf = yaml.load(open(argv[1]))
    card = Image(argv[2])
    for label, box in conf.iteritems():
        card.drawRectangle(x=box['x'], y=box['y'], w=box['w'], h=box['h'], color=Color.BLACK)
        field = card.crop(x=box['x'], y=box['y'], w=box['w'], h=box['h'])
        if 'binarize' not in box.keys():
            field = field.whiteBalance().grayscale().binarize()
        field_text = tesserocr.image_to_text(field.getPIL()).strip().split("\n")[0]
        try:
            card.drawText("{}: {}".format(label, field_text), x=box['x']+10, y=box['y'], color=Color.RED)
        except:
            print 'Failed to draw {}'.format(label)
            print field_text
            continue

    card.save('draw_fields.png')
    # card.show()

if __name__ == "__main__":
    main(sys.argv)
