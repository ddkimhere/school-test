from pathlib import Path

path = Path('index.html')
raw = path.read_bytes()
nl = '\r\n' if b'\r\n' in raw else '\n'
text = raw.decode('utf-8')


def norm(s: str) -> str:
    return s.replace('\n', nl)


def replace_once(old: str, new: str, label: str):
    global text
    old_n = norm(old)
    new_n = norm(new)
    if old_n not in text:
        raise SystemExit(f'Patch target not found: {label}')
    text = text.replace(old_n, new_n, 1)

replace_once(
    ".paper { background: white; padding: 25px 30px; border: 1px solid #d9e0e8; border-radius: 8px; max-width: 800px; margin: 20px auto 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }",
    ".paper { background: white; padding: 25px 30px; border: 1px solid #d9e0e8; border-radius: 8px; max-width: 800px; margin: 20px auto 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; display: flex; flex-direction: column; min-height: 1120px; }",
    'screen paper layout',
)
replace_once(
    ".paper-footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 18px; padding-top: 7px; border-top: 1px solid #aeb8c4; color: #6b7280; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; }",
    ".paper-footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: auto; padding-top: 7px; border-top: 1px solid #aeb8c4; color: #6b7280; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; }",
    'screen footer margin',
)
replace_once(
    ".q-container { display: block; }",
    ".q-container { display: block; flex: 1 0 auto; }",
    'question container flex',
)
replace_once(
    ".paper { box-shadow: none; border: none; padding: 0; max-width: 100%; margin: 0; }",
    ".paper { box-shadow: none; border: none; padding: 0; max-width: 100%; margin: 0; display: flex; flex-direction: column; min-height: 281mm; }",
    'print paper layout',
)
replace_once(
    ".paper-footer { color: #000; border-top-color: #000; margin-top: 12px; }",
    ".paper-footer { color: #000; border-top-color: #000; margin-top: auto; }",
    'print footer margin',
)

path.write_bytes(text.encode('utf-8'))
print('Footer-bottom patch applied with original line endings preserved')
