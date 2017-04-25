#!/usr/bin/env python2
from SimpleCV import *
import shutil
import logging
import json

PROPERTY_VERBOSE = 'verbose'
PROPERTY_DEBUG = 'debug'
PROPERTY_FORMAT = 'format'
PROPERTY_EXPORT = 'export'

class CardScan:
    def __init__(self, props):
        if isinstance(props, dict):
            self.format = props[PROPERTY_FORMAT]
            self.debug = props[PROPERTY_DEBUG]
            self.verbose = props[PROPERTY_VERBOSE]
            self.export = props[PROPERTY_EXPORT]
        else: # assumed to be args object
            self.format = props.format
            self.debug = props.debug
            self.verbose = props.verbose
            self.export = props.export

        #     logging.warning('Creating {0} object without properties (dict), will create with default values')
        #     self.props = {
        #         PROPERTY_FORMAT: 'yaml',
        #         PROPERTY_DEBUG: True,
        #         PROPERTY_VERBOSE: True
        #     }
        # else:
        #     self.props = props

        self.card_parsers = []
        # self.register_card("nl.government.idcard")
        # self.register_card("nl.government.drivinglicence")
        self.register_card('gov.ca.driver_license')

    def register_card(self, dn):
        dn = "card." + dn
        class_name = dn.split(".")[-1]
        mod = __import__(dn, fromlist=[class_name])
        card_class = getattr(mod, class_name)
        self.card_parsers.append(card_class({
            PROPERTY_DEBUG: True,
            PROPERTY_EXPORT: True
        }))
        if self.verbose:
            print("Added detection class {}".format(dn))

    def parse(self, id_filename, pic_filename):
        input_image = Image(id_filename)

        # Create new empty debug directory if debug is enabled
        # TODO debug images to s3
        if self.debug:
            # if os.path.isdir("debug"):
            #     shutil.rmtree("debug")
            # os.mkdir("debug")
            input_image.save("debug/input.png")

        # Use blob detection to find all cards in the scanned document
        input_image_inverse = input_image.invert()
        cards = input_image_inverse.findBlobs(threshval=10, minsize=50)
        if self.verbose:
            print("Detected {} blobs".format(len(cards)))

        # Normalize card rotation
        normalized_cards = []
        for idx, card in enumerate(cards):
            card.rotate(card.angle())
            normalized = card.hullImage().invert()
            normalized_cards.append(normalized)
            if self.debug:
                normalized.save("debug/normalized_{}.png".format(idx))

        #TODO Move matching between selfie and card portrait somewhere else, leave only card/template match here
        selfie = Image(pic_filename)
        # Run all registered card classes against all detected blobs
        matches = []
        for ncard in normalized_cards:
            if self.verbose:
                print("Running testers for blob")
            for tester in self.card_parsers:
                if self.verbose:
                    print("  Running tester: {}".format(tester.name))
                match = tester.match(ncard, selfie)
                if match != None:
                    if self.verbose:
                        print("    Tester matched!")
                    matches.append(match)
                    break

        # Output results
        if self.verbose:
            print "Output format: {}".format(self.format)

        if self.format == "json":
            json_report = json.dumps(matches)
            return json_report

        if self.format == "yaml":
            import yaml

            return yaml.dump(matches)

        return json.dumps(matches)


if __name__ == "__main__":
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
    parsed = cardscan.parse(args.filename, args.picture)
    print parsed