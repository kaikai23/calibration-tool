import cv2
image = cv2.imread('images/template.jpg')
window_name = 'Image'
color = (0, 0, 255)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (0, 0, 255)
font_thickness = 1
# predefined_corners = {
#     0: [84, 109],  # 00: top-left
#     1: [875, 109],  # 01: top-right
#     2: [84, 688],  # 02: bottom-left
#     3: [875, 688],  # 03: bottom-right
#     4: [351, 109],  # 04: mid-top-left
#     5: [608, 109],  # 05: mid-top-right
#     6: [351, 415],  # 06: mid-bottom-left
#     7: [608, 415],  # 07: mid-bottom-right
#     8: [412, 175],  # 08: arc-left
#     9: [546, 175],  # 09: arc-right
#     10: [340, 203],  # 10: mid-left-cross1
#     11: [340, 251],  # 11: mid-left-cross2
#     12: [340, 272],  # 12: mid-left-cross3
#     13: [340, 321],  # 13: mid-left-cross4
#     14: [340, 369],  # 14: mid-left-cross5
#     15: [619, 203],  # 15: mid-right-cross1
#     16: [619, 252],  # 16: mid-right-cross2
#     17: [619, 272],  # 17: mid-right-cross3
#     18: [619, 321],  # 18: mid-right-cross4
#     19: [619, 369],  # 19: mid-right-cross5
# }
predefined_corners = {
    0: [0, 0],  # 00: top-left
    1: [1500, 0],  # 01: top-right
    2: [0, 1100],  # 02: bottom-left
    3: [1500, 1100],  # 03: bottom-right
    4: [505, 0],  # 04: mid-top-left
    5: [995, 0],  # 05: mid-top-right
    6: [505, 580],  # 06: mid-bottom-left
    7: [995, 580],  # 07: mid-bottom-right
    8: [625, 120],  # 08: arc-left
    9: [875, 120],  # 09: arc-right
    10: [505, 175],  # 10: mid-left-cross1
    11: [505, 260],  # 11: mid-left-cross2
    12: [505, 300],  # 12: mid-left-cross3
    13: [505, 385],  # 13: mid-left-cross4
    14: [505, 470],  # 14: mid-left-cross5
    15: [995, 175],  # 15: mid-right-cross1
    16: [995, 260],  # 16: mid-right-cross2
    17: [995, 300],  # 17: mid-right-cross3
    18: [995, 385],  # 18: mid-right-cross4
    19: [995, 470],  # 19: mid-right-cross5
    20: [90, 0],
    21: [1410, 0]
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


cv2.imwrite('images/template_corners1.png', image)

