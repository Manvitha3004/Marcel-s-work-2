import json, os, re, urllib.request, zipfile
import fitz

zip_path = r'C:\Users\manvi\OneDrive\Desktop\DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0_PACKAGE.zip'
with zipfile.ZipFile(zip_path) as z:
    pdf_name = 'DTL_ST_REPRO_001_Protocol_Candidate_v0_1_0.pdf'
    out = os.path.join('verification', 'taskA', 'computations', 'protocol_candidate_text.txt')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pdf_bytes = z.read(pdf_name)
    with open(os.path.join('verification', 'taskA', 'computations', 'protocol_candidate.pdf'), 'wb') as f:
        f.write(pdf_bytes)
    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    text = '\n'.join(page.get_text('text') for page in doc)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print('protocol_text_len', len(text))

# Download arXiv abstract page and PDF metadata check
url = 'https://arxiv.org/abs/2610.30266'
with urllib.request.urlopen(url, timeout=30) as r:
    html = r.read().decode('utf-8', 'replace')
    print('arxiv_status', r.status)
    print('contains_DTL', 'Discrete time liquids' in html)
    print('first_800_chars=', html[:800])

pdf_url = 'https://arxiv.org/pdf/2610.30266.pdf'
with urllib.request.urlopen(pdf_url, timeout=30) as r:
    data = r.read()
    open(os.path.join('verification', 'taskA', 'computations', 'arxiv_2610_30266.pdf'), 'wb').write(data)
    print('arxiv_pdf_bytes', len(data))
