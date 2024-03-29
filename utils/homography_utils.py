from typing import Optional, Tuple
import cv2
import numpy as np
from .opencv_utils import MousePointsClick, OpenCVWindow
from predefined_corners import predefined_corners
import tkinter as tk


def get_h_from_images(
    image: np.ndarray,
    pts_size: int = 5,
    color: Tuple[int, int, int] = (255, 0, 0),
    num_rect_pts=4,
) -> Optional[np.ndarray]:

    min_required_pts = 4
    pts1 = []  # video frame points
    pts2 = []  # template points
    pt_ids = []  # chosen template point ids

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
        pt_ids.append(clicked_num)
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

    if len(pts1) == min_required_pts and len(pts2) == min_required_pts:
        h0 = cv2.getPerspectiveTransform(pts2, pts1)
    else:
        # with ransac
        h0, _ = cv2.findHomography(pts2, pts1)

    return h0, pts1, pts2, pt_ids


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
