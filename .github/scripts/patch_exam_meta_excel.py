from pathlib import Path

path = Path("index.html")
raw = path.read_bytes()
nl = "\r\n" if b"\r\n" in raw else "\n"
text = raw.decode("utf-8")


def n(s: str) -> str:
    return s.replace("\n", nl)


def replace_once(old: str, new: str, label: str):
    global text
    old_n = n(old)
    new_n = n(new)
    if old_n not in text:
        raise SystemExit(f"Patch target not found: {label}")
    text = text.replace(old_n, new_n, 1)


# 1) 시험지 상단 교과서/Unit 표시용 스타일
replace_once(
    """    .paper-instruction { font-size: 17px; font-weight: bold; color: #1e293b; margin: 0; }\n    \n    .student-info-box { display: flex; gap: 20px; font-size: 13.5px; font-weight: bold; color: #334155; align-items: center; }""",
    """    .paper-instruction { font-size: 17px; font-weight: bold; color: #1e293b; margin: 0; }\n    .paper-meta { font-size: 13px; font-weight: bold; color: #475569; margin: 0 0 6px 0; letter-spacing: 0.1px; }\n    \n    .student-info-box { display: flex; gap: 20px; font-size: 13.5px; font-weight: bold; color: #334155; align-items: center; }""",
    "paper meta css",
)

replace_once(
    """      .paper-header-row { border-bottom-color: #000; margin-bottom: 8px; padding-bottom: 4px; }\n      .student-info-box { color: #000; }""",
    """      .paper-header-row { border-bottom-color: #000; margin-bottom: 8px; padding-bottom: 4px; }\n      .paper-meta { color: #000; }\n      .student-info-box { color: #000; }""",
    "paper meta print css",
)

# 2) DB 편집기: 단어 선택 시 엑셀 다운로드 버튼 표시
replace_once(
    '<select id="dbEditorCategory" onchange="refreshDbEditorFilters()">',
    '<select id="dbEditorCategory" onchange="refreshDbEditorFilters(); updateDbExcelButton()">',
    "db editor category onchange",
)

replace_once(
    """        <button type=\"button\" onclick=\"refreshDbEditorFilters()\" style=\"padding:10px 14px; background:#475569; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;\">🔄 목록 새로고침</button>\n        <button type=\"button\" onclick=\"renameDbTextbook()\" style=\"padding:10px 14px; background:#7c3aed; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;\">✏️ 교과서 이름 변경</button>""",
    """        <button type=\"button\" onclick=\"refreshDbEditorFilters()\" style=\"padding:10px 14px; background:#475569; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;\">🔄 목록 새로고침</button>\n        <button id=\"dbExcelBtn\" type=\"button\" onclick=\"downloadDbWordsExcel()\" style=\"display:none; padding:10px 14px; background:#107c41; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;\">⬇️ 단어 엑셀 다운로드</button>\n        <button type=\"button\" onclick=\"renameDbTextbook()\" style=\"padding:10px 14px; background:#7c3aed; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;\">✏️ 교과서 이름 변경</button>""",
    "excel download button",
)

# 3) 엑셀 다운로드 기능: 외부 라이브러리 없이 Excel XML(.xls) 생성
replace_once(
    """    function getEditorCollectionName() {\n      return document.getElementById('dbEditorCategory').value === \"sentence\" ? \"sentences\" : \"words\";\n    }\n\n    async function refreshDbEditorFilters(preferredTb = \"\", preferredLesson = \"\") {""",
    """    function getEditorCollectionName() {\n      return document.getElementById('dbEditorCategory').value === \"sentence\" ? \"sentences\" : \"words\";\n    }\n\n    function updateDbExcelButton() {\n      const btn = document.getElementById('dbExcelBtn');\n      if (!btn) return;\n      btn.style.display = document.getElementById('dbEditorCategory').value === \"vocab\" ? \"inline-block\" : \"none\";\n    }\n\n    function escapeXml(value) {\n      return String(value ?? \"\")\n        .replace(/&/g, \"&amp;\")\n        .replace(/</g, \"&lt;\")\n        .replace(/>/g, \"&gt;\")\n        .replace(/\"/g, \"&quot;\")\n        .replace(/'/g, \"&apos;\");\n    }\n\n    async function downloadDbWordsExcel() {\n      if (!auth.currentUser) return alert(\"관리자 로그인이 필요합니다.\");\n      if (document.getElementById('dbEditorCategory').value !== \"vocab\") {\n        return alert(\"데이터 종류에서 [단어]를 선택해 주세요.\");\n      }\n\n      const tb = document.getElementById('dbEditorTb').value;\n      const lesson = Number(document.getElementById('dbEditorLesson').value);\n      if (!tb || !Number.isFinite(lesson)) return alert(\"교과서와 과를 선택해 주세요.\");\n\n      let latestWords;\n      try {\n        latestWords = await fetchLatestWordsFromDB(tb, lesson);\n      } catch (err) {\n        return alert(\"단어 데이터를 불러오지 못했습니다: \" + err.message);\n      }\n\n      if (!latestWords || latestWords.length === 0) {\n        return alert(`${tb} ${lesson}과에 저장된 단어가 없습니다.`);\n      }\n\n      if (!dbWordMap[tb]) dbWordMap[tb] = {};\n      dbWordMap[tb][lesson] = latestWords;\n      const words = getSortedWords(tb, lesson);\n\n      const header = [\"교과서\", \"Unit\", \"번호\", \"영단어\", \"뜻\"];\n      const rows = words.map(item => [tb, lesson, item.displayNum, item.word, item.meaning]);\n\n      const xmlRow = (cells, headerRow = false) => {\n        const cellXml = cells.map((value, index) => {\n          const isNumber = !headerRow && (index === 1 || index === 2) && Number.isFinite(Number(value));\n          const type = isNumber ? \"Number\" : \"String\";\n          const style = headerRow ? ' ss:StyleID=\"Header\"' : '';\n          return `<Cell${style}><Data ss:Type=\"${type}\">${escapeXml(value)}</Data></Cell>`;\n        }).join(\"\");\n        return `<Row>${cellXml}</Row>`;\n      };\n\n      const workbookXml = `<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?mso-application progid=\"Excel.Sheet\"?>\n<Workbook xmlns=\"urn:schemas-microsoft-com:office:spreadsheet\"\n xmlns:o=\"urn:schemas-microsoft-com:office:office\"\n xmlns:x=\"urn:schemas-microsoft-com:office:excel\"\n xmlns:ss=\"urn:schemas-microsoft-com:office:spreadsheet\"\n xmlns:html=\"http://www.w3.org/TR/REC-html40\">\n <Styles>\n  <Style ss:ID=\"Header\">\n   <Font ss:Bold=\"1\"/>\n   <Interior ss:Color=\"#D9EAD3\" ss:Pattern=\"Solid\"/>\n  </Style>\n </Styles>\n <Worksheet ss:Name=\"Unit ${lesson}\">\n  <Table>\n   <Column ss:Width=\"110\"/>\n   <Column ss:Width=\"55\"/>\n   <Column ss:Width=\"45\"/>\n   <Column ss:Width=\"150\"/>\n   <Column ss:Width=\"220\"/>\n   ${xmlRow(header, true)}\n   ${rows.map(row => xmlRow(row)).join(\"\n   \")}\n  </Table>\n </Worksheet>\n</Workbook>`;\n\n      const blob = new Blob([workbookXml], { type: \"application/vnd.ms-excel;charset=utf-8\" });\n      const url = URL.createObjectURL(blob);\n      const a = document.createElement('a');\n      const safeTb = tb.replace(/[\\/:*?\"<>|]/g, \"_\");\n      a.href = url;\n      a.download = `${safeTb}_Unit${lesson}_단어목록.xls`;\n      document.body.appendChild(a);\n      a.click();\n      a.remove();\n      URL.revokeObjectURL(url);\n    }\n\n    async function refreshDbEditorFilters(preferredTb = \"\", preferredLesson = \"\") {""",
    "excel export functions",
)

replace_once(
    """      const category = document.getElementById('dbEditorCategory').value;\n      const collectionName = category === \"sentence\" ? \"sentences\" : \"words\";""",
    """      const category = document.getElementById('dbEditorCategory').value;\n      updateDbExcelButton();\n      const collectionName = category === \"sentence\" ? \"sentences\" : \"words\";""",
    "toggle excel button during refresh",
)

# 4) 생성되는 시험지에 교과서명 + Unit 표시
replace_once(
    """      topBar.appendChild(printBtn);\n      paper.appendChild(topBar);\n\n      const instructions = {""",
    """      topBar.appendChild(printBtn);\n      paper.appendChild(topBar);\n\n      const examTb = document.getElementById('genTb').value;\n      const examLesson = document.getElementById('genLesson').value;\n      const metaDiv = document.createElement('div');\n      metaDiv.className = \"paper-meta\";\n      metaDiv.innerText = `교과서: ${examTb}  ·  Unit ${examLesson}`;\n      paper.appendChild(metaDiv);\n\n      const instructions = {""",
    "paper textbook and unit meta",
)

path.write_bytes(text.encode("utf-8"))
print("Patch applied successfully")
