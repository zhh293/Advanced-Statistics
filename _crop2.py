from PIL import Image
im = Image.open('_pdfpages/p171_0_Im171.png').convert('RGB')
w, h = im.size
im.crop((0, int(h*0.78), w, h)).save('_pdfpages/_q8start.png')
im2 = Image.open('_pdfpages/p172_0_Im172.png').convert('RGB')
w2, h2 = im2.size
im2.crop((0, 0, w2, int(h2*0.45))).save('_pdfpages/_q8cont.png')
print('done')
