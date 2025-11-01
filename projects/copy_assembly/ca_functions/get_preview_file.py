from projects.copy_assembly.settings import PROJECT_ROOT
import os
from PIL import Image


def get_bytes_png_from_inventor_file(filepath) -> bytes:
    with open(filepath, 'rb') as fin:
        sourcedata = fin.read()

    start = sourcedata.index(b'PNG')
    end = sourcedata.index(b'IEND\xaeB`')

    byte_arr = sourcedata[start - 1: end + len(b'IEND\xaeB`')]

    return byte_arr

def save_png(name_image, data_bytes: bytes) -> str:
    img = Image.frombytes(data=data_bytes, size=(512, 512), mode='RGB')
    path_image = os.path.join(PROJECT_ROOT, 'resources', 'prepared_assembly', 'image', f'{name_image}.png')
    img.save(path_image)
    return path_image

def save_png_2(name_image, data_bytes: bytes) -> str:
    path_image = os.path.join(PROJECT_ROOT, 'resources', 'prepared_assembly', 'image', f'tmp_{name_image}.png')
    with open(path_image, 'wb') as image:
        image.write(data_bytes)
    
    img = Image.open(path_image)
    img.save(os.path.join(PROJECT_ROOT, 'resources', 'prepared_assembly', 'image', f'{name_image}.png'), format='PNG')
    del img
    os.remove(path_image)
    return path_image


if __name__ == '__main__':
    path = r'\\PDM\PKODocs\Inventor Project\ООО ЛебедяньМолоко\1642_24\4.2. УРП ALS.P.01.02.01.A\05 проект INVENTOR\ALS.1642.4.2.01.03.00.000-Лоток\ALS.1642.4.2.01.03.00.000.iam'
    b = get_bytes_png_from_inventor_file(path)
    pi = save_png_2('aaa', b)
    print(pi)
