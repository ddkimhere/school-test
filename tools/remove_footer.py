from pathlib import Path

path = Path('index.html')
with open(path, 'r', encoding='utf-8', newline='') as f:
    text = f.read()

nl = '\r\n' if '\r\n' in text else '\n'

def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once(
    "    .paper { background: white; padding: 25px 30px; border: 1px solid #d9e0e8; border-radius: 8px; max-width: 800px; margin: 20px auto 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; display: flex; flex-direction: column; min-height: 1120px; }",
    "    .paper { background: white; padding: 25px 30px; border: 1px solid #d9e0e8; border-radius: 8px; max-width: 800px; margin: 20px auto 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }",
    'screen paper layout'
)
replace_once(
    "    .paper-footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: auto; padding-top: 7px; border-top: 1px solid #aeb8c4; color: #6b7280; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; }" + nl,
    "",
    'footer css'
)
replace_once(
    "    .q-container { display: block; flex: 1 0 auto; }",
    "    .q-container { display: block; }",
    'question container flex'
)
replace_once(
    "      .paper { box-shadow: none; border: none; padding: 0; max-width: 100%; margin: 0; display: flex; flex-direction: column; min-height: 281mm; }",
    "      .paper { box-shadow: none; border: none; padding: 0; max-width: 100%; margin: 0; }",
    'print paper layout'
)
replace_once(
    "      .paper-footer { color: #000; border-top-color: #000; margin-top: auto; }" + nl,
    "",
    'print footer css'
)

footer_block = nl.join([
    "      paper.appendChild(container);",
    "",
    "      const footer = document.createElement('div');",
    "      footer.className = \"paper-footer\";",
    "      const footerBrand = document.createElement('span');",
    "      footerBrand.innerText = \"YMS ENGLISH · BUSONG\";",
    "      const footerMeta = document.createElement('span');",
    "      footerMeta.innerText = `${examTb} · UNIT ${examLesson}`;",
    "      footer.appendChild(footerBrand);",
    "      footer.appendChild(footerMeta);",
    "      paper.appendChild(footer);",
])
replace_once(footer_block, "      paper.appendChild(container);", 'footer renderer')

if '.paper-footer' in text or "const footer = document.createElement('div');" in text:
    raise SystemExit('footer remnants remain')

with open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(text)
