import glob, os
from PIL import Image
for f in sorted(glob.glob('_pdfpages/*.tiff')):
    im = Image.open(f)
    out = f.replace('.tiff', '.png')
    # upscale a bit for OCR readability
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')
    im.save(out)
    print('converted', out, im.size)
