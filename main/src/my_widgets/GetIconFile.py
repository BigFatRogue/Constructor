def get_preview_file(filepath) -> bytes:
    with open(filepath, 'rb') as fin:
        sourcedata = fin.read()

    start = sourcedata.index(b'PNG')
    end = sourcedata.index(b'IEND\xaeB`')

    byte_arr = sourcedata[start - 1: end + len(b'IEND\xaeB`')]

    return byte_arr





