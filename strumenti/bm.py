"""Immagini .BM di Harvester: larghezza u32, altezza u32, u32 (ignorato), pixel 8 bit.
Tavolozze .PAL: 768 byte RGB (0-63 o 0-255)."""
import struct
from PIL import Image

def read_pal(data):
    p = list(data[:768])
    if max(p) < 64:
        p = [v * 255 // 63 for v in p]
    return p

def bm_to_image(data, pal):
    w, h = struct.unpack_from('<II', data, 0)
    im = Image.frombytes('P', (w, h), bytes(data[12:12 + w * h]))
    im.putpalette(pal)
    return im

def image_to_bm(im, hdr):
    """im: immagine 'P' gia' nella tavolozza giusta; hdr: header originale (12 byte)."""
    w, h = im.size
    out = bytearray(hdr[:12])
    struct.pack_into('<II', out, 0, w, h)
    return bytes(out) + im.tobytes()
