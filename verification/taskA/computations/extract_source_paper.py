import os, re
import fitz

pdf_path = os.path.join('verification', 'taskA', 'computations', 'arxiv_2610_30266.pdf')
doc = fitz.open(pdf_path)
print('pages', doc.page_count)
texts = []
for i in range(min(doc.page_count, 8)):
    txt = doc[i].get_text('text')
    texts.append(txt)
all_text = '\n'.join(texts)
for kw in ['J = 5', 'lambda', 'M_osc', 'k_B', 'L = 100', 'theta_init', 'D = 2', 'omega_c', 'tau_osc', 'T0', '5/gamma', 'y(t)']:
    idx = all_text.find(kw)
    print('\nKW=', kw, 'INDEX=', idx)
    if idx >= 0:
        snippet = all_text[max(0, idx-200):idx+600]
        print(snippet)
