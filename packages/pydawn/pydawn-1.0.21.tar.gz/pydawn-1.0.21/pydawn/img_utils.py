# coding=utf-8
import os
from PIL import Image

def dhash(image, hash_size = 8):
    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
                    (hash_size + 1, hash_size),
                    Image.LANCZOS,
                    )
    #pixels = list(image.getdata())

    # Compare adjacent pixels.
    difference = []
    for row in xrange(hash_size):
        for col in xrange(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)
    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return ''.join(hex_string)


def calc_distance(dhash1, dhash2):
    difference = (int(dhash1, 16)) ^ (int(dhash2, 16))
    return bin(difference).count("1")


if __name__ == '__main__':
    dhash_1 = str(dhash(Image.open("D:\\ai\\fake_img\\0F7B8658FDC98DD64DC5018D8C32BF03.png")))
    dhash_2 = str(dhash(Image.open("D:\\ai\\fake_img\\499DC96BE6167DED3580605434CACF33.png")))
    print dhash_1
    print dhash_2
    print calc_distance(dhash_1, dhash_2)

    '''
    img_dir = "D:\\ai\\fake_img\\"
    dhash_dict = {}
    for file_name in os.listdir(img_dir):
        file_path = os.path.join(img_dir, file_name)
        dhash_value = str(dhash(Image.open(file_path)))
        dhash_dict[file_name] = dhash_value

    result_dict = {}
    for key0, value0 in dhash_dict.items():
        for key1, value1 in dhash_dict.items():
            if key0 == key1:
                continue
            distance = calc_distance(value0, value1)
            result_dict["%s,%s" % (key0, key1)] = distance

    sorted_burst_dict = sorted(result_dict.iteritems(), key=lambda d: d[1], reverse=False)

    result = open("python_distance_bi_raw.csv", "w+")

    for item in sorted_burst_dict:
        result.write("%s,%s\n" % (item[0], item[1]))

    result.close()
    '''
