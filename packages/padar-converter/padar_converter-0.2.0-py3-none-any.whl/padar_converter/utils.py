import chardet


def detect_encoding(file_path):
    data = open(file_path, "rb").read()
    encoding = chardet.detect(data)
    if encoding['encoding'] == 'utf-8':
        return 'utf-8-sig'
    else:
        return encoding['encoding']
