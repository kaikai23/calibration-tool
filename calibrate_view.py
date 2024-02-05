import os
import argparse

import cv2
import numpy as np

from src.homography.homography_utils import get_h_from_images, transform
from src.opencv_utils import MousePointsClick, OpenCVWindow

import tkinter as tk
from predefined_corners import predefined_corners


def _to_filename(camera):
    return (
        camera.replace("\\", "")
        .replace(".", "")
        .replace("-", "")
        .replace("@", "")
        .replace(":", "")
        .replace("/", "")
    )


def calibrate(frame, pav_img, h_file, camera, max_num_pts=4):
    h, pts1, pts2 = get_h_from_images(frame, pav_img, num_rect_pts=max_num_pts)

    pts1_file = f"data/pts1__view_{_to_filename(camera)}.npy"
    pts2_file = f"data/pts2__view_{_to_filename(camera)}.npy"

    np.save(h_file, h)
    np.save(pts1_file, pts1)
    np.save(pts2_file, pts2)

    return h


def get_draw_pts(frame, num_pts=30):
    w = OpenCVWindow(f"Get max #{num_pts}")
    mpc = MousePointsClick(w, num_pts)
    mpc.get_points(w, frame, pts_size=20)
    draw_pts = np.asarray(mpc.points)
    return draw_pts


def transform(points, homography):
    points = np.asarray(points)
    if homography is not None:
        res = cv2.perspectiveTransform(
            np.asarray(points).reshape((-1, 1, 2)).astype(np.float32), homography
        )
        out_pts: np.ndarray = res.reshape(points.shape).astype(int)
        return out_pts
    return None


def main(args):

    assert os.path.isfile(args.input), f"File not found: {args.input}"
    assert os.path.isfile(args.plane), f"File not found: {args.plane}"

    camera = args.input
    floor = cv2.imread(args.plane)

    wname = "frame"
    wname_p = "template"

    cap = cv2.VideoCapture(camera)

    assert cap.isOpened(), f'Unable to open the camera: "{camera}"!'

    ret, frame = cap.read()
    if not ret:
        raise NotImplementedError()

    cv2.namedWindow(wname, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(wname, 512, 512)

    h_file = f"data/h__cam_{_to_filename(camera)}.npy"
    draw_pts = {}

    h = None
    if os.path.isfile(h_file):
        h = np.load(h_file)

    ori_frame = frame.copy()
    overlay = frame.copy()

    while True:
        cv2.imshow(wname, frame)
        cv2.imshow(wname_p, floor)
        key = cv2.waitKey(10)

        if h is None and key == -1:
            h = calibrate(frame, floor, h_file, camera)
            print(f'Homography is {h}')
        if h is not None:
            draw_pts = {id: transform(pt, h) for id, pt in predefined_corners.items()}

        # Exit
        elif key == ord("q"):
            break

        # Draw in original image
        for id, pt in draw_pts.items():
            cv2.circle(overlay, tuple(pt), 5, (0, 0, 255), -1)
            cv2.line(overlay, tuple(draw_pts[0]), tuple(draw_pts[1]), (255, 0, 0), 3)
            cv2.line(overlay, tuple(draw_pts[1]), tuple(draw_pts[3]), (255, 0, 0), 3)
            cv2.line(overlay, tuple(draw_pts[3]), tuple(draw_pts[2]), (255, 0, 0), 3)
            cv2.line(overlay, tuple(draw_pts[2]), tuple(draw_pts[0]), (255, 0, 0), 3)
            cv2.line(overlay, tuple(draw_pts[4]), tuple(draw_pts[6]), (255, 0, 0), 3)
            cv2.line(overlay, tuple(draw_pts[6]), tuple(draw_pts[7]), (255, 0, 0), 3)
            cv2.line(overlay, tuple(draw_pts[7]), tuple(draw_pts[5]), (255, 0, 0), 3)
        alpha = 0.45
        frame = cv2.addWeighted(overlay, alpha, ori_frame, 1 - alpha, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="The input video file")
    parser.add_argument("plane", type=str, help="The plane image file")
    args = parser.parse_args()
    root = tk.Tk()

    print("*" * 200)
    print("*")
    print(
        "Press C to calibrate, D to draw points in order to show the calibration accuracy"
    )
    print("*")
    print("*" * 200)

    main(args)
