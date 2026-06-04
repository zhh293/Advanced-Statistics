from pypdf import PdfReader
r = PdfReader('[BOOK]统计学习导论 基于R应用-高清中文.pdf')
print('pages:', len(r.pages))
def walk(outs, depth=0):
    for o in outs:
        if isinstance(o, list):
            walk(o, depth+1)
        else:
            try:
                pg = r.get_destination_page_number(o)
            except Exception:
                pg = '?'
            print('  '*depth + str(o.title) + '  -> p' + str(pg))
try:
    walk(r.outline)
except Exception as e:
    print('outline err', e)
