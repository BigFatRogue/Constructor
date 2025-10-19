def get_preview_file(filepath):
    with open(filepath, 'rb') as fin:
        sourcedata = fin.read()

    start = sourcedata.index(b'PNG')
    end = sourcedata.index(b'IEND\xaeB`')

    byte_arr = sourcedata[start - 1: end + len(b'IEND\xaeB`')]

    return byte_arr


if __name__ == '__main__':
    import os
    import time

    main_path = r'C:\Users\p.golubev\Downloads'
    filename = r'_132S_TOP 29 5,5 Solid C C H 2 NY.ipt'
    full_path = os.path.join(main_path, filename)

    with open(full_path, 'rb') as file_it:
        ipt_bytes = file_it.read()
        with open(f'{main_path}\\new_file_ipt.ipt', 'wb') as new_file_it:
            new_file_it.write(ipt_bytes)

    img_bytes = get_preview_file(f'{main_path}\\new_file_ipt.ipt')
    with open(f'{main_path}\\tmp.png', 'wb') as image:
        image.write(img_bytes)