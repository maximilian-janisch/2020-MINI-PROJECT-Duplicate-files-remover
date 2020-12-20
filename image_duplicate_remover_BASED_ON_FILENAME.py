"""
This removes duplicate images AND OTHER FILES **JUST BASED ON THEIR FILENAME**: Two files are considered identical
if there exists a natural number n such that the n+1-st character of the name of one of the files is a "(", there is no
"(" in that string before the n+1-st place,
and the first n characters of both file names are identical. Additionally, if two file names are identical, they are also
considered identical, even though there might be no "(" in either name.

For example, "hello.txt" and "hello(1).txt" or "hello(10).txt" and "hello(20).txt" would be considered duplicates or
"""

import os

from classes import DuplicateRemover


class ImageDuplicateRemoverFILENAME(DuplicateRemover):
    def check_duplicate(self, file_path1, file_path2):
        """Returns whether file_path1 and file_path2 indicate identical images according to the rule described above."""
        file_path1, file_path2 = os.path.basename(file_path1), os.path.basename(file_path2)
        if "(" in file_path1:
            index = file_path1.index("(")
        elif "(" in file_path2:
            index = file_path2.index("(")
        elif file_path1 == file_path2:
            print("hi")
            return True
        else:
            return False

        return file_path1[:index] == file_path2[:index]

    def get_best_file_from_class(self, file_class):
        best_img = max(file_class, key=lambda img: jpg_res(img)[0] * jpg_res(img)[1])
        return best_img


def jpg_res(filename):
    """Returns resolution in (width, height) of the JPG image called `filename`."""
    with open(filename, 'rb') as img_file:
        # height of image (in 2 bytes) is at 164th position
        img_file.seek(163)
        # read the 2 bytes
        a = img_file.read(2)
        # calculate height
        height = (a[0] << 8) + a[1]
        # next 2 bytes is width
        a = img_file.read(2)
        # calculate width
        width = (a[0] << 8) + a[1]

    return width, height


if __name__ == '__main__':
    remover = ImageDuplicateRemoverFILENAME(directory="C:\\Users\\Maximilian\\Desktop")
    remover()
