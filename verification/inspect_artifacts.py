import importlib.util, json, os, sys, zipfile

pdfs = [
    r'C:\Users\manvi\OneDrive\Desktop\DTL_ST_Manvitha_Energy_Root_Cause_Audit_v0_1_0.pdf',
    r'C:\Users\manvi\OneDrive\Desktop\DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0.pdf',
    r'C:\Users\manvi\OneDrive\Desktop\Spiral_Time_Mathematical_Core_v0_3_1_for_Manvitha.pdf',
]
zip_path = r'C:\Users\manvi\OneDrive\Desktop\DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0_PACKAGE.zip'
print('MODULES')
for name in ['fitz','PyMuPDF','pdfplumber','pypdf','reportlab']:
    print(name, bool(importlib.util.find_spec(name)))
print('PDF_EXISTS')
for p in pdfs:
    print(os.path.exists(p), p)
print('ZIP_EXISTS', os.path.exists(zip_path), zip_path)
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        print('ZIP_N', len(names))
        for n in names[:20]:
            print(n)
