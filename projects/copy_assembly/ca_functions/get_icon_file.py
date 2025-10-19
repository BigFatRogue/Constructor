import ctypes
from ctypes import wintypes
from PIL import Image

# Constants for Shell32
SHGFI_ICON = 0x000000100
SHGFI_LARGEICON = 0x000000000
SHGFI_SMALLICON = 0x000000001
SHGFI_USEFILEATTRIBUTES = 0x000000010


def error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as error:
            ...
    return wrapper


# Define SHFILEINFO structure
class SHFILEINFO(ctypes.Structure):
    _fields_ = [
        ("hIcon", wintypes.HICON),
        ("iIcon", wintypes.INT),
        ("dwAttributes", wintypes.DWORD),
        ("szDisplayName", wintypes.CHAR * 260),
        ("szTypeName", wintypes.CHAR * 80)
    ]


# Define ICONINFO structure
class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", wintypes.BOOL),
        ("xHotspot", wintypes.DWORD),
        ("yHotspot", wintypes.DWORD),
        ("hbmMask", wintypes.HBITMAP),
        ("hbmColor", wintypes.HBITMAP)
    ]


# Define BITMAP structure
class BITMAP(ctypes.Structure):
    _fields_ = [
        ("bmType", wintypes.LONG),
        ("bmWidth", wintypes.LONG),
        ("bmHeight", wintypes.LONG),
        ("bmWidthBytes", wintypes.LONG),
        ("bmPlanes", wintypes.WORD),
        ("bmBitsPixel", wintypes.WORD),
        ("bmBits", ctypes.c_void_p)
    ]


@error_wrapper
def get_file_icon(file_path, save_path, large=True):
    shfi = SHFILEINFO()
    flags = SHGFI_ICON | SHGFI_USEFILEATTRIBUTES | (SHGFI_LARGEICON if large else SHGFI_SMALLICON)

    # Call SHGetFileInfo to get the icon
    result = ctypes.windll.shell32.SHGetFileInfoW(
        file_path,
        0,
        ctypes.byref(shfi),
        ctypes.sizeof(shfi),
        flags
    )

    if not result:
        raise FileNotFoundError(f"Cannot find icon for {file_path}")

    # Get the icon bitmap
    hdc = ctypes.windll.user32.GetDC(0)
    hdc_mem = ctypes.windll.gdi32.CreateCompatibleDC(hdc)

    icon_info = ICONINFO()
    ctypes.windll.user32.GetIconInfo(shfi.hIcon, ctypes.byref(icon_info))

    bmpinfo = BITMAP()
    ctypes.windll.gdi32.GetObjectW(icon_info.hbmColor, ctypes.sizeof(bmpinfo), ctypes.byref(bmpinfo))

    hbmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, bmpinfo.bmWidth, bmpinfo.bmHeight)
    ctypes.windll.gdi32.SelectObject(hdc_mem, hbmp)
    ctypes.windll.user32.DrawIconEx(hdc_mem, 0, 0, shfi.hIcon, bmpinfo.bmWidth, bmpinfo.bmHeight, 0, None, 0x0003)

    bmp_bits = ctypes.create_string_buffer(bmpinfo.bmWidth * bmpinfo.bmHeight * 4)
    ctypes.windll.gdi32.GetBitmapBits(hbmp, len(bmp_bits), bmp_bits)

    img = Image.frombuffer(
        'RGBA',
        (bmpinfo.bmWidth, bmpinfo.bmHeight),
        bmp_bits,
        'raw',
        'BGRA',
        0,
        1
    )

    img.save(save_path, 'PNG')
    img.resize((img.size[0] * 2, img.size[1]))

    # Cleanup
    ctypes.windll.user32.DestroyIcon(shfi.hIcon)
    ctypes.windll.gdi32.DeleteObject(icon_info.hbmColor)
    ctypes.windll.gdi32.DeleteObject(icon_info.hbmMask)
    ctypes.windll.gdi32.DeleteObject(hbmp)
    ctypes.windll.gdi32.DeleteDC(hdc_mem)
    ctypes.windll.user32.ReleaseDC(0, hdc)


# if __name__ == "__main__":
#     file_path = r'C:\Users\p.golubev\Desktop\Пробники Inventor\GolubevInventorProjcet.ipj'  # Замените на путь к вашему файлу
#     save_path = r"Icon.png"  # Замените на путь для сохранения изображения
#     get_file_icon(file_path, save_path, large=True)  # large=True для больших иконок, large=False для маленьких
