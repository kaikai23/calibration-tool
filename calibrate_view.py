import os
import argparse

import cv2
import numpy as np

from utils.homography_utils import get_h_from_images, transform

import tkinter as tk
from predefined_corners import predefined_corners


def _to_filename(camera):
    return (
        camera.replace("\\", "-")
        .replace(".", "")
        .replace("-", "")
        .replace("@", "")
        .replace(":", "")
        .replace("/", "-")
    )


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

    h_file = f"data/h_{_to_filename(camera)}.npy"
    pts1_file = f"data/pts1_{_to_filename(camera)}.npy"
    pts2_file = f"data/pts2_{_to_filename(camera)}.npy"
    pt_ids_file = f"data/pt_ids_{_to_filename(camera)}.npy"
    draw_pts = {}

    h = pts1 = pts2 = pt_ids = None
    if os.path.isfile(h_file):
        h = np.load(h_file)
        pts1 = np.load(pts1_file)
        pts2 = np.load(pts2_file)
        pt_ids = list(np.load(pt_ids_file))
        print('Loaded previous homography')

    ori_frame = frame.copy()
    overlay = frame.copy()
    global refine
    refine = False
    while True:
        cv2.imshow(wname, frame)
        cv2.imshow(wname_p, floor)
        key = cv2.waitKey(10)

        if h is not None:
            draw_pts = {id: transform(pt, h) for id, pt in predefined_corners.items()}

        if h is None and key == -1:
            h, pts1, pts2, pt_ids = get_h_from_images(frame, num_rect_pts=4)
            print(f'points1: {pts1}, points2: {pts2}')
            print(f'Homography is {h}')


        # Adjust points
        elif key == 13 or refine:  # 13:"Enter"
            assert h is not None
            refine = True
            root = tk.Tk()
            root.title("Choose point id to adjust")
            label = tk.Label(root, text="1. Click point id you want to adjuste\n "
                                        "2. Press ↑↓←→ arrows to adjust\n "
                                        "3. Press 'Enter' and click next point\n "
                                        "4. Click 'Finish' when you want to stop"
                                        , font=("Helvetica", 14))
            label.pack()
            button_list = []
            num_buttons = len(predefined_corners)
            global clicked_num
            def on_button_click(key):
                global clicked_num
                global refine
                button = button_list[key]
                if button['text'] == 'Finish':
                    print('Finish refinement')
                    refine = False
                else:
                    clicked_num = int(button['text'])
                    print(f'{clicked_num} is clicked')
                root.quit()
            # create buttons
            for key in range(num_buttons):
                button = tk.Button(root, text=str(key), command=lambda k=key: on_button_click(k))
                button.pack()
                button_list.append(button)
            button = tk.Button(root, text='Finish', command=lambda k=-1: on_button_click(k))
            button.pack()
            button_list.append(button)
            root.mainloop()
            root.destroy()
            while True and refine:
                key = cv2.waitKey(0)
                if key in [81, 2]:  # "←"
                    shift = np.array([-1, 0])
                elif key in [82, 0]:  # "↑"
                    shift = np.array([0, -1])
                elif key in [83, 3]:  # "→"
                    shift = np.array([1, 0])
                elif key in [84, 1]:  # "↓"
                    shift = np.array([0, 1])
                elif key == 13:  # "Enter"
                    print('next point')
                    break
                else:
                    print(f'{key}, continue')
                    continue
                if clicked_num in pt_ids:
                    i = pt_ids.index(clicked_num)
                    pts1[i] = pts1[i] + shift
                else:
                    p2 = predefined_corners[clicked_num]
                    p1 = transform(p2, h)
                    p1 = p1 + shift
                    pts1 = np.vstack((pts1[1:], p1))
                    pts2 = np.vstack((pts2[1:], p2))
                    pt_ids = pt_ids[1:] + [clicked_num]
                pts1 = np.asarray(pts1, dtype=np.float32)
                pts2 = np.asarray(pts2, dtype=np.float32)
                h = cv2.getPerspectiveTransform(pts2, pts1)
                print(f'points1: {pts1}, points2: {pts2}')
                print(f'Homography is {h}')
                draw_pts = {id: transform(pt, h) for id, pt in predefined_corners.items()}
                overlay = ori_frame.copy()
                cv2.line(overlay, tuple(draw_pts[0]), tuple(draw_pts[1]), (255, 0, 0), 2)
                cv2.line(overlay, tuple(draw_pts[1]), tuple(draw_pts[3]), (255, 0, 0), 2)
                cv2.line(overlay, tuple(draw_pts[3]), tuple(draw_pts[2]), (255, 0, 0), 2)
                cv2.line(overlay, tuple(draw_pts[2]), tuple(draw_pts[0]), (255, 0, 0), 2)
                cv2.line(overlay, tuple(draw_pts[4]), tuple(draw_pts[6]), (255, 0, 0), 2)
                cv2.line(overlay, tuple(draw_pts[6]), tuple(draw_pts[7]), (255, 0, 0), 2)
                cv2.line(overlay, tuple(draw_pts[7]), tuple(draw_pts[5]), (255, 0, 0), 2)
                alpha = 0.45
                frame = cv2.addWeighted(overlay, alpha, ori_frame, 1 - alpha, 0)
                for id, pt in draw_pts.items():
                    cv2.circle(frame, tuple(pt), 2, (0, 0, 255), -1)
                cv2.imshow(wname, frame)


        # Exit
        elif key == ord("q"):
            break
        elif key == ord("s"):
            np.save(h_file, h)
            np.save(pts1_file, pts1)
            np.save(pts2_file, pts2)
            np.save(pt_ids_file, pt_ids)
            print(f'saved to {pts1_file}\n{pts2_file}\n{h_file}\n{pt_ids_file}')

        # Draw in original image
        for id, pt in draw_pts.items():
            cv2.circle(overlay, tuple(pt), 2, (0, 0, 255), -1)
            cv2.line(overlay, tuple(draw_pts[0]), tuple(draw_pts[1]), (255, 0, 0), 2)
            cv2.line(overlay, tuple(draw_pts[1]), tuple(draw_pts[3]), (255, 0, 0), 2)
            cv2.line(overlay, tuple(draw_pts[3]), tuple(draw_pts[2]), (255, 0, 0), 2)
            cv2.line(overlay, tuple(draw_pts[2]), tuple(draw_pts[0]), (255, 0, 0), 2)
            cv2.line(overlay, tuple(draw_pts[4]), tuple(draw_pts[6]), (255, 0, 0), 2)
            cv2.line(overlay, tuple(draw_pts[6]), tuple(draw_pts[7]), (255, 0, 0), 2)
            cv2.line(overlay, tuple(draw_pts[7]), tuple(draw_pts[5]), (255, 0, 0), 2)
        alpha = 0.45
        frame = cv2.addWeighted(overlay, alpha, ori_frame, 1 - alpha, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="The input video file")
    parser.add_argument("--plane", type=str, default='images/template_corners.png', help="The plane image file")
    args = parser.parse_args()
    root_ = tk.Tk()
    root_.title('main')
    label = tk.Label(root_, text="流程\n"
                                 "1.选择图片与模版的4个对应点\n"
                                 "(若已有保存值，会自动跳过此步,直接显示蓝色球场线)\n"
                                 "2.微调4个对应点的位置：Enter键\n"
                                 "3.保存/覆盖存档：S键\n"
                                 "4.退出：Q键"
                     , font=("Helvetica", 14))
    label.pack()

    print("*" * 200)
    print("*")
    print(
        "Press C to calibrate, D to draw points in order to show the calibration accuracy"
    )
    print("*")
    print("*" * 200)

    main(args)
