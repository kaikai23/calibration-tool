import cv2
image = cv2.imread('images/court_template.png')
window_name = 'Image'
color = (255, 0, 0)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (255, 255, 255)
font_thickness = 1
predefined_corners = {
    0: [210, 158],  # 00: top-left
    1: [744, 158],  # 01: top-right
    2: [210, 550],  # 02: bottom-left
    3: [744, 550],  # 03: bottom-right
    4: [390, 158],  # 04: mid-top-left
    5: [564, 158],  # 05: mid-top-right
    6: [390, 365],  # 06: mid-bottom-left
    7: [564, 365],  # 07: mid-bottom-right
    8: [433, 214],  # 08: arc-left
    9: [521, 214],  # 09: arc-right
    10: [389, 220],  # 10: mid-left-cross1
    11: [387, 251],  # 11: mid-left-cross2
    12: [387, 265],  # 12: mid-left-cross3
    13: [389, 295],  # 13: mid-left-cross4
    14: [389, 325],  # 14: mid-left-cross5
    15: [566, 220],  # 15: mid-right-cross1
    16: [567, 251],  # 16: mid-right-cross2
    17: [567, 265],  # 17: mid-right-cross3
    18: [566, 295],  # 18: mid-right-cross4
    19: [566, 325],  # 19: mid-right-cross5
}
radius = 1
thickness = 1
for idx, coord in predefined_corners.items():
    image = cv2.circle(image, coord, radius, color, thickness)

    text = str(idx)
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_x = coord[0] - text_size[0] // 2
    text_y = coord[1] - radius - 5  # Adjust the vertical position as needed
    image = cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, font_thickness)


cv2.imwrite('images/predefined_corners.png', image)

