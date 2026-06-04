import os
from pypdf import PdfReader
r = PdfReader('[BOOK]统计学习导论 基于R应用-高清中文.pdf')
os.makedirs('_pdfpages', exist_ok=True)
# 5.4 习题 p168 (1-indexed in outline) -> python index 167; next chapter p212
# extract embedded images from pages 166..180 (0-indexed)
for pi in range(166, 182):
    page = r.pages[pi]
    imgs = page.images
    for j, img in enumerate(imgs):
        name = f'_pdfpages/p{pi+1}_{j}_{img.name}'
        with open(name, 'wb') as f:
            f.write(img.data)
        print('saved', name, len(img.data))
