#!/usr/bin/env python3

from PIL import Image
import csv
import sys
import math

WHITE = (255, 255, 255)

# Keep the max color delta <= 10 for best results
MAX_COLOR_DELTA = 10
COLOR_STEP = 8

MAX_CSV_COLUMNS = 16384
PIXEL_DELIMITER = ','
FRAME_DELIMITER = 'R'
SEQUENCE_END = 'E'

COLOR_APPROXIMATION_CACHE = {}


def process_image(original_img, size):
    frames = []
    frame_count = original_img.n_frames
    for frame_num in range(frame_count):
        original_img.seek(frame_num)
        frame = Image.new('RGB', original_img.size, WHITE)
        frame.paste(original_img)
        resized_frame = frame.resize(size)
        frames.append(resized_frame)

    return frames


def dist(a, b):
    (x1, y1, z1) = a
    (x2, y2, z2) = b

    x_diff_squared = (x1 - x2) ** 2
    y_diff_squared = (y1 - y2) ** 2
    z_diff_squared = (z1 - z2) ** 2

    return math.sqrt(x_diff_squared + y_diff_squared + z_diff_squared)


def round_value(val, step):
    mod = val % step
    if mod == 0:
        return (val, val)

    delta_up = step - mod
    delta_down = mod
    return (val + delta_up, val - delta_down)


def clamp(val, min, max):
    if val > max:
        return max
    elif val < min:
        return min
    else:
        return val


def adjacent_colors(color):
    (r, g, b) = color

    result = []
    for adj_r in round_value(r, COLOR_STEP):
        for adj_g in round_value(g, COLOR_STEP):
            for adj_b in round_value(b, COLOR_STEP):
                result.append((clamp(adj_r, 0, 255), clamp(
                    adj_g, 0, 255), clamp(adj_b, 0, 255)))

    return result


def approximate_color(color):
    if color in COLOR_APPROXIMATION_CACHE:
        return COLOR_APPROXIMATION_CACHE[color]

    best = None
    for approx_color in adjacent_colors(color):
        distance = dist(color, approx_color)
        if best is None or distance < best[0]:
            best = (distance, approx_color)

    COLOR_APPROXIMATION_CACHE[color] = best[1]
    return best[1]


def to_csv(frames):
    def color_to_vba_long(color):
        (r, g, b) = color
        color_long = (b << 16) + (g << 8) + r
        return str(color_long)

    def color_to_str(color):
        return '%s-%s-%s' % color

    def action(frame, row, col, color):
        return '|'.join((str(row), str(col), color_to_vba_long(color)))

    write_csv(frames, 'data.csv', action)


def pixel_at(frame, row, col):
    if frame is None:
        return None
    else:
        return frame.getpixel((col, row))


def buffer_add(buffer, writer, value):
    if len(buffer) == MAX_CSV_COLUMNS:
        writer.writerow(buffer)
        return []
    else:
        return buffer + [value]


def write_csv(frames, name, action):
    width = frames[0].width
    height = frames[0].height

    with open(name, 'w') as file:
        writer = csv.writer(file, delimiter=PIXEL_DELIMITER)
        last_frame = None
        buffer = []
        for frame in frames:
            for row in range(height):
                for col in range(width):
                    color = approximate_color(frame.getpixel((col, row)))
                    last_color = None
                    if last_frame is not None:
                        last_color = approximate_color(last_frame.getpixel(
                            (col, row)))

                    if last_color is None or dist(color, last_color) >= MAX_COLOR_DELTA:
                        buffer = buffer_add(
                            buffer, writer, action(frame, row, col, color))

            buffer = buffer_add(buffer, writer, FRAME_DELIMITER)
            last_frame = frame

        buffer = buffer_add(buffer, writer, SEQUENCE_END)
        if len(buffer) > 0:
            writer.writerow(buffer)
            buffer = []


def main():
    args = sys.argv

    if len(args) < 2 or len(args) > 4:
        print('Usage:\n  img_name [width] [height]' % args[0], file=sys.stderr)
        sys.exit(1)

    # Open the image file
    img = Image.open(args[1])

    # Determine the desired resoulution of the output
    size = (img.width, img.height)
    if len(args) == 4:
        size = (int(args[2]), int(args[3]))

    print('Generating %d output frames of size %sx%s ... ' %
          (img.n_frames, size[0], size[1]), end='')
    sys.stdout.flush()

    frames = process_image(img, size)

    print('done')
    print("Writing output files ... ", end='')
    sys.stdout.flush()

    to_csv(frames)

    print('done')


if __name__ == '__main__':
    main()
