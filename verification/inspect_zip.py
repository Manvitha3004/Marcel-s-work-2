import zipfile

zip_path = r'C:\Users\manvi\OneDrive\Desktop\DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0_PACKAGE.zip'
with zipfile.ZipFile(zip_path) as z:
    names = z.namelist()
    print('FILES', names)
    for name in names:
        if name.endswith(('.md', '.txt', '.json', '.csv', '.tex')):
            print('\n###', name)
            data = z.read(name).decode('utf-8', 'replace')
            print(data[:5000])
