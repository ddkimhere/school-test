from pathlib import Path
p = Path('index.html')
text = p.read_text(encoding='utf-8')
text = text.replace('\r\n', '\n').replace('\r', '\n')
p.write_bytes(text.replace('\n', '\r\n').encode('utf-8'))
print('normalized index.html to CRLF')
