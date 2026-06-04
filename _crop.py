from PIL import Image
# p171 lower half (Q8 start), p172 upper (Q8 cont + Q9), p170 (Q3-Q7), p171 upper (Q7-8)
jobs = [
    ('_pdfpages/p170_0_Im170.png', 0.0, 0.6, '_q34567'),
    ('_pdfpages/p171_0_Im171.png', 0.5, 1.0, '_q78'),
    ('_pdfpages/p172_0_Im172.png', 0.0, 0.8, '_q89'),
]
for src, top, bot, name in jobs:
    im = Image.open(src).convert('RGB')
    w, h = im.size
    im.crop((0, int(h*top), w, int(h*bot))).save('_pdfpages/'+name+'.png')
    print('saved', name)
