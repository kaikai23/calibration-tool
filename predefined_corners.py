import cv2
image = cv2.imread('images/template.jpg')
window_name = 'Image'
color = (0, 0, 255)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (0, 0, 255)
font_thickness = 1
predefined_corners = {
    0: [80, 105],  # 00: top-left
    1: [879, 105],  # 01: top-right
    2: [80, 692],  # 02: bottom-left
    3: [879, 692],  # 03: bottom-right
    4: [352, 108],  # 04: mid-top-left
    5: [609, 108],  # 05: mid-top-right
    6: [352, 414],  # 06: mid-bottom-left
    7: [609, 415],  # 07: mid-bottom-right
    8: [413, 177],  # 08: arc-left
    9: [546, 177],  # 09: arc-right
    10: [340, 201],  # 10: mid-left-cross1
    11: [340, 251],  # 11: mid-left-cross2
    12: [340, 271],  # 12: mid-left-cross3
    13: [340, 319],  # 13: mid-left-cross4
    14: [340, 369],  # 14: mid-left-cross5
    15: [620, 201],  # 15: mid-right-cross1
    16: [620, 252],  # 16: mid-right-cross2
    17: [620, 273],  # 17: mid-right-cross3
    18: [620, 319],  # 18: mid-right-cross4
    19: [620, 367],  # 19: mid-right-cross5
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


cv2.imwrite('images/template_corners.png', image)

