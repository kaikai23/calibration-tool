from typing import Optional, Tuple
import cv2
import numpy as np
from ..opencv_utils import MousePointsClick, OpenCVWindow
from ..geometry import Rx, Ry, Rz
from predefined_corners import predefined_corners
import tkinter as tk
import time


def compute_homography_from_points(
    pts1: np.ndarray, pts2: np.ndarray, frame_width: int, frame_height: int
) -> Tuple[np.ndarray, int, int, int, int]:

    pts1 = np.asarray(pts1).astype(np.float32).reshape(-1, 1, 2)
    pts2 = np.asarray(pts2).astype(np.float32).reshape(-1, 1, 2)

    # Compute the default perspective transform H0
    h0 = cv2.getPerspectiveTransform(pts1, pts2)

    # Transform the corners of the input image using H0, and compute the minimum and maximum values
    # for the x and y coordinates of these corners. Let's denote them xmin, xmax, ymin, ymax.
    tlc = np.array([0, 0], np.float32)
    trc = np.array([frame_width, 0], np.float32)
    blc = np.array([0, frame_height], np.float32)
    brc = np.array([frame_width, frame_height], np.float32)

    tlc_t = cv2.perspectiveTransform(
        tlc.reshape((-1, 1, 2)).astype(np.float32), h0)
    trc_t = cv2.perspectiveTransform(
        trc.reshape((-1, 1, 2)).astype(np.float32), h0)
    blc_t = cv2.perspectiveTransform(
        blc.reshape((-1, 1, 2)).astype(np.float32), h0)
    brc_t = cv2.perspectiveTransform(
        brc.reshape((-1, 1, 2)).astype(np.float32), h0)

    big_array = np.concatenate((tlc_t, trc_t, blc_t, brc_t), axis=None)
    x = big_array[::2]
    xmin, xmax = int(round(np.nanmin(x))), int(round(np.nanmax(x)))
    y = big_array[1::2]
    ymin, ymax = int(round(np.nanmin(y))), int(round(np.nanmax(y)))

    # Compute the translation necessary to map the point (xmin,ymin) to (0,0)
    t = np.array([[1, 0, -xmin], [0, 1, -ymin], [0, 0, 1]], np.float32)

    # Compute the optimised perspective transform H1 = T*H0 and specify an output image size of
    # (xmax-xmin) x (ymax-ymin).
    h1 = t.dot(h0)

    return h1, xmax, xmin, ymax, ymin


def get_h_from_images(
    image: np.ndarray,
    pavillion: np.ndarray,
    pts_size: int = 5,
    color: Tuple[int, int, int] = (255, 0, 0),
    num_rect_pts=4,
) -> Optional[np.ndarray]:

    min_required_pts = 4
    pts1 = []  # video frame points
    pts2 = []  # template points

    root = tk.Tk()
    root.title("Choose point id in template")
    label = tk.Label(root, text="Choose correspondence point in template", font=("Helvetica", 14))
    label.pack()
    button_list = []
    num_buttons = len(predefined_corners)
    global clicked_num
    def on_button_click(key):
        global clicked_num
        button = button_list[key]
        clicked_num = int(button['text'])
        print(f'{clicked_num} is clicked')
        root.quit()
        button.pack_forget()  # Hide the clicked button
        # buttons_alive.remove(key)
    for key in range(num_buttons):
        button = tk.Button(root, text=str(key), command=lambda k=key: on_button_click(k))
        button.pack()
        button_list.append(button)
    for _ in range(num_rect_pts):
        root.mainloop()
        pts2.append(predefined_corners[clicked_num])
        frame_calibration_window = OpenCVWindow("Image")
        correspondences_1 = MousePointsClick(
            frame_calibration_window, 1)
        correspondences_1.get_points(
            frame_calibration_window, image, pts_size=pts_size, color=color
        )
        pts1.append(correspondences_1.points[0])
    root.destroy()

    if len(pts1) < min_required_pts:
        print(
            f"Not enough points selected for window {frame_calibration_window.opencv_winname}. Exiting"
        )
        return None
    else:
        print(f"Points from image 1: {pts1}")



    if len(pts2) < min_required_pts:
        print(
            f"Not enough points selected for window {frame_calibration_window.opencv_winname}. Exiting"
        )
    else:
        print(f"Points from image 2: {pts2}")

    # Get H from points
    pts1 = np.asarray(pts1, dtype=np.float32)
    pts2 = np.asarray(pts2, dtype=np.float32)

    # h0 = cv2.getPerspectiveTransform(pts2, pts1)

    # h0, _, _, _, _ = compute_homography_from_points(pts2, pts1, img.shape[1], img.shape[0])
    if (
        len(pts1) == min_required_pts
        and len(pts2) == min_required_pts
    ):
        h0 = cv2.getPerspectiveTransform(pts2, pts1)
    else:
        # with ransac
        h0, _ = cv2.findHomography(pts2, pts1)

    return h0, pts1, pts2


def transform(points, homography):
    if homography is not None:
        res = cv2.perspectiveTransform(
            np.asarray(points).reshape(
                (-1, 1, 2)).astype(np.float32), homography
        )
        out_pts: np.ndarray = res.reshape(points.shape).astype(np.int)
        return out_pts
    return None


def cameraPoseFromHomography(H):
    H1 = H[:, 0]
    H2 = H[:, 1]
    H3 = np.cross(H1, H2)

    norm1 = np.linalg.norm(H1)
    norm2 = np.linalg.norm(H2)
    tnorm = (norm1 + norm2) / 2.0

    T = H[:, 2] / tnorm
    return np.mat([H1, H2, H3, T])


def get_auto_h(img_shape, deg=45, height=9):
    # img_plane_2d = np.meshgrid(np.arange(img_shape[0]), np.arange(img_shape[1]), sparse=False)

    # img_plane_3d = np.stack((img_plane_2d[0][0], img_plane_2d[1][0], np.ones(img_shape[0]))).T

    #r = Rz(np.radians(45))
    # r = Rx(np.radians(45))
    #r = Ry(np.radians(45))

    # rotated = img_plane_3d @ r
    return None
