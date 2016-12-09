#!/usr/bin/env python2

import cv2
import numpy as np
from matplotlib import image as image
from SimpleCV import Image

def detect_card_contour(img):
    '''
    Crops out image of card
    :param img:
    :return:
    '''
    # Create gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
    # retrieves only the extreme outer contours
    contours, hierarchy = cv2.findContours(thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE);

    area = [cv2.contourArea(cnt) for cnt in contours]
    card_contour = contours[area.index(max(area))]

    return None


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


if __name__ == "__main__":
    import argparse

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", help="path to the image file")
    # ap.add_argument("-c", "--coords",
    #             help="comma seperated list of source points")
    args = vars(ap.parse_args())

    # load the image and grab the source coordinates (i.e. the list of
    # of (x, y) points)
    # NOTE: using the 'eval' function is bad form, but for this example
    # let's just roll with it -- in future posts I'll show you how to
    # automatically determine the coordinates without pre-supplying them
    image = cv2.imread(args["image"])
    # pts = np.array(eval(args["coords"]), dtype="float32")

    BINARY_THRESHOLD = 150
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE);

    area = [cv2.contourArea(cnt) for cnt in contours]
    card_contour = contours[area.index(max(area))]

    # Get minimum enclosing rectangle
    # pts = np.array(cv2.cv.BoxPoints(cv2.minAreaRect(card_contour)))

    # Get approximate poly
    pts = np.array([p[0] for p in cv2.approxPolyDP(card_contour, 0.00001 * cv2.arcLength(card_contour, True), True)])

    # apply the four point tranform to obtain a "birds eye view" of the image
    warped = four_point_transform(image, pts)
    print u'warped image shape = {0:s}'.format(warped.shape)
    height, width, channels = warped.shape

    template = cv2.imread("data/gov/ca/dmv/template.jpg")
    print u'template size = {0:s}'.format(template.shape)
    print u'resizing to x={0:f}, y={0:f}'.format(float(template.shape[1]) / width,float(template.shape[1]) * 0.6305637982 / height)

    # scale the warped image to match template
    warped = cv2.resize(warped, (0,0), fx=float(template.shape[1]) / width, fy = float(template.shape[1]) * 0.6305637982 / height, interpolation = cv2.INTER_CUBIC)
    print u'after resizing, warped image shape = {0:s}'.format(warped.shape)

    # show the original and warped images
    cv2.imshow("Original", cv2.resize(image, (0,0), fx=0.2, fy=0.2 ))
    # cv2.imshow("Warped", cv2.resize(warped, (0,0), fx=0.2, fy=0.2 * 0.6305637982 * width / height))
    cv2.imshow('Warped', cv2.resize(warped, (0,0), fx=1, fy=1))
    cv2.waitKey(0)

    print "now trying to match template ... "
    # Convert OpenCV image to SimpleCV images
    # Look at the code of the Image Class it stupidly does the transform TWICE effectively doing nothing.
    # So you have to do the following
    #    transImg=img.transpose(1,0,2) # transpose the rows and columns
    #    transColImg=transImg[:,:,::-1] # change from BGR to RGB
    #    simpleCVImg=Image(transColImg)
    simple_warped = Image(warped.transpose(1,0,2)[:,:,::-1])
    simple_template = Image(template)

    res = simple_warped.findTemplate(template_image=simple_template, threshold=2.5)

    # Test parsing out with OCR with tesserocr package
    pil_im = simple_warped.crop(x=385, y=309, w=386, h=36).getPIL()
    pil_im.show()
    import tesserocr

    print tesserocr.tesseract_version()  # print tesseract-ocr version
    print tesserocr.get_languages()  # prints tessdata path and list of available languages
    print tesserocr.image_to_text(pil_im)  # print ocr text from image


    # field = simple_warped.crop(x=385, y=389, w=386, h=36)
    # field = field.whiteBalance()
    # field = field.grayscale() * 1.2  # Convert to grayscale and increase brightness
    # field = field.binarize()
    # try:
    #     field_text = field.readText().strip().split("\n")[0] # Run tesseract OCR and cleanup result
    # except:
    #     field_text = ""

    # print field_text

    ## template matching with cv2
    #
    # res = cv2.matchTemplate(warped, template, cv2.TM_CCOEFF)
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # print min_val, max_val, min_loc, max_loc
    # h = template.shape[0]
    # w = template.shape[1]
    # top_left = max_loc
    # bottom_right = (top_left[0] + w, top_left[1] + h)
    # print top_left, bottom_right
    # warped_copy = warped.copy()
    # cv2.rectangle(warped_copy,top_left, bottom_right, 255, 2)
    # cv2.imshow('Matched', warped_copy)
    # cv2.waitKey(0)

    print res

    print "Confirming a different template image won't match"

    false_template = Image('data/nl/government/idcard/template.png')
    print simple_warped.findTemplate(template_image=false_template, threshold=2.5)
    # template matching with cv2
    # false_template = cv2.imread('data/nl/government/idcard/template.png')
    # res = cv2.matchTemplate(warped, false_template, cv2.TM_CCOEFF)
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # print min_val, max_val, min_loc, max_loc
    # h = false_template.shape[0]
    # w = false_template.shape[1]
    # top_left = max_loc
    # bottom_right = (top_left[0] + w, top_left[1] + h)
    # print top_left, bottom_right
    # warped_copy = warped.copy()
    # cv2.rectangle(warped_copy,top_left, bottom_right, 255, 2)
    # cv2.imshow('False match', warped_copy)
    # cv2.waitKey(0)





