#!/usr/bin/env python3

from PIL import Image
import csv
import sys
# import math

# COLOR_STEP = 64
# COLOR_DELIMITER = ','
PIXEL_DELIMITER = ','


def index_colors(img):
    palette = img.getpalette()
    num_colors = len(palette)//3
    color_index = []

    for i in range(num_colors):
        red = palette[i]
        green = palette[i+1]
        blue = palette[i+2]
        color_index.append((red, green, blue))

    return color_index


def extract_frames(gif):
    frames = []
    for frame_num in range(gif.n_frames):
        gif.seek(frame_num)
        frame = Image.new("RGB", gif.size)
        frame.paste(gif)
        frames.append(frame)

    return frames


# def approximate_value(val, step):
#     mod = val % step
#     if mod == 0:
#         return val

#     delta_up = step - mod
#     delta_down = mod

#     if delta_up < delta_down:
#         return val + delta_up
#     else:
#         return val - delta_down


# def round_value(val, step):
#     mod = val % step
#     if mod == 0:
#         return (val, val)

#     delta_up = step - mod
#     delta_down = mod
#     return (val + delta_up, val - delta_down)


# def dist(a, b):
#     (x1, y1, z1) = a
#     (x2, y2, z2) = b

#     x_diff_squared = (x1 - x2) ** 2
#     y_diff_squared = (y1 - y2) ** 2
#     z_diff_squared = (z1 - z2) ** 2

#     return math.sqrt(x_diff_squared + y_diff_squared + z_diff_squared)

# def adjacent_colors(color):
#     (r, g, b) = color

#     result = []
#     for adj_r in round_value(r, COLOR_STEP):
#         for adj_b in round_value(g, COLOR_STEP):
#             for adj_g in round_value(b, COLOR_STEP):
#                 result.append(adj_r, adj_b, adj_g)

#     return result


# def round_color(color, color_step):
#     (r, g, b) = color
#     return (approximate_value(r, color_step), approximate_value(g, color_step), approximate_value(b, color_step))


# def color_to_str(color):
#     (r, g, b) = color
#     return str(r) + COLOR_DELIMITER + str(g) + COLOR_DELIMITER + str(b)


def to_csv(frames, name):
    width = frames[0].width
    height = frames[0].height

    with open(name + '-r.csv', 'w') as r_file, open(name + '-g.csv', 'w') as g_file, open(name + '-b.csv', 'w') as b_file:
        r_writer = csv.writer(r_file, delimiter=PIXEL_DELIMITER)
        g_writer = csv.writer(g_file, delimiter=PIXEL_DELIMITER)
        b_writer = csv.writer(b_file, delimiter=PIXEL_DELIMITER)

        for row in range(height):
            for col in range(width):
                csv_row_r = []
                csv_row_g = []
                csv_row_b = []

                for frame in frames:
                    (r, g, b) = frame.getpixel((col, row))
                    csv_row_r.append(str(r))
                    csv_row_g.append(str(g))
                    csv_row_b.append(str(b))

                r_writer.writerow(csv_row_r)
                g_writer.writerow(csv_row_g)
                b_writer.writerow(csv_row_b)


def main():
    args = sys.argv

    if len(args) != 2:
        print("Usage:\n  " + args[0] + " gif_name", file=sys.stderr)
        sys.exit(1)

    gif = Image.open(args[1])
    frames = extract_frames(gif)
    to_csv(frames, "data")


if __name__ == '__main__':
    main()
