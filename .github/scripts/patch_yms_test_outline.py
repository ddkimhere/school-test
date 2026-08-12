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


# 1) YMS 전용 시험지 헤더/푸터 스타일
replace_once(
    """    .paper { background: white; padding: 25px 30px; border-radius: 8px; max-width: 800px; margin: 20px auto 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }\n    .paper-header-row { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #000; padding-bottom: 6px; margin-bottom: 12px; }\n    .paper-instruction { font-size: 17px; font-weight: bold; color: #1e293b; margin: 0; }\n    .paper-meta { font-size: 13px; font-weight: bold; color: #475569; margin: 0 0 6px 0; letter-spacing: 0.1px; }\n    \n    .student-info-box { display: flex; gap: 20px; font-size: 13.5px; font-weight: bold; color: #334155; align-items: center; }\n    .info-item { border-bottom: 1px solid #000; padding: 0 10px 1px 10px; display: inline-block; }""",
    """    .paper { background: white; padding: 25px 30px; border: 1px solid #d9e0e8; border-radius: 8px; max-width: 800px; margin: 20px auto 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }\n    .yms-brand-strip { display: flex; justify-content: space-between; align-items: center; border-top: 5px solid #163a63; border-bottom: 1px solid #9aa8b6; padding: 10px 0 8px; margin-bottom: 0; }\n    .yms-brand-name { font-size: 20px; line-height: 1; font-weight: 900; letter-spacing: 1.2px; color: #163a63; }\n    .yms-brand-name span { font-size: 10px; font-weight: 700; letter-spacing: 2.8px; color: #64748b; margin-left: 7px; vertical-align: 2px; }\n    .yms-test-type { font-size: 10px; font-weight: 800; letter-spacing: 1.2px; color: #334155; border: 1px solid #9aa8b6; border-radius: 999px; padding: 4px 10px; white-space: nowrap; }\n    .paper-meta { font-size: 17px; font-weight: 800; color: #172b4d; margin: 10px 0 8px 0; letter-spacing: 0.15px; }\n    .paper-header-row { display: flex; justify-content: space-between; align-items: center; gap: 18px; border-left: 4px solid #163a63; background: #f5f7fa; padding: 9px 12px; margin-bottom: 15px; }\n    .paper-instruction { font-size: 14px; font-weight: 700; color: #1e293b; margin: 0; line-height: 1.4; }\n    \n    .student-info-box { display: flex; gap: 18px; font-size: 12.5px; font-weight: 700; color: #334155; align-items: center; white-space: nowrap; }\n    .info-item { border-bottom: 1px solid #334155; padding: 0 10px 1px 10px; display: inline-block; }\n    .paper-footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 18px; padding-top: 7px; border-top: 1px solid #aeb8c4; color: #6b7280; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; }""",
    "YMS test paper CSS",
)

replace_once(
    """      .paper { box-shadow: none; padding: 0; max-width: 100%; margin: 0; }\n      .paper-header-row { border-bottom-color: #000; margin-bottom: 8px; padding-bottom: 4px; }\n      .paper-meta { color: #000; }\n      .student-info-box { color: #000; }""",
    """      .paper { box-shadow: none; border: none; padding: 0; max-width: 100%; margin: 0; }\n      .yms-brand-strip { border-top-color: #000; border-bottom-color: #000; padding-top: 8px; padding-bottom: 7px; }\n      .yms-brand-name, .yms-brand-name span, .yms-test-type, .paper-meta { color: #000; }\n      .yms-test-type { border-color: #000; }\n      .paper-header-row { background: #fff; border-left-color: #000; margin-bottom: 10px; padding: 7px 10px; }\n      .paper-instruction, .student-info-box { color: #000; }\n      .info-item { border-bottom-color: #000; }\n      .paper-footer { color: #000; border-top-color: #000; margin-top: 12px; }""",
    "YMS print CSS",
)

# 2) 시험지 상단을 YMS 고유 헤더로 변경
replace_once(
    """      const examTb = document.getElementById('genTb').value;\n      const examLesson = document.getElementById('genLesson').value;\n      const metaDiv = document.createElement('div');\n      metaDiv.className = \"paper-meta\";\n      metaDiv.innerText = `교과서: ${examTb}  ·  Unit ${examLesson}`;\n      paper.appendChild(metaDiv);\n\n      const instructions = {""",
    """      const examTb = document.getElementById('genTb').value;\n      const examLesson = document.getElementById('genLesson').value;\n      const testTypeLabels = {\n        \"1\": \"SENTENCE · TRANSLATION\",\n        \"2\": \"WRITING TEST\",\n        \"3\": \"WORD ORDER TEST\",\n        \"4\": \"CLOZE TEST\",\n        \"w1\": \"VOCABULARY TEST\",\n        \"w2\": \"VOCABULARY TEST\",\n        \"w3\": \"VOCABULARY · MIXED\"\n      };\n\n      const brandStrip = document.createElement('div');\n      brandStrip.className = \"yms-brand-strip\";\n\n      const brandName = document.createElement('div');\n      brandName.className = \"yms-brand-name\";\n      brandName.innerHTML = `YMS <span>ENGLISH</span>`;\n\n      const testType = document.createElement('div');\n      testType.className = \"yms-test-type\";\n      testType.innerText = testTypeLabels[qType] || \"ENGLISH TEST\";\n\n      brandStrip.appendChild(brandName);\n      brandStrip.appendChild(testType);\n      paper.appendChild(brandStrip);\n\n      const metaDiv = document.createElement('div');\n      metaDiv.className = \"paper-meta\";\n      metaDiv.innerText = `${examTb}  ·  UNIT ${examLesson}`;\n      paper.appendChild(metaDiv);\n\n      const instructions = {""",
    "YMS paper header markup",
)

# 3) 시험지 하단 브랜드 푸터
replace_once(
    """      paper.appendChild(container);\n    }""",
    """      paper.appendChild(container);\n\n      const footer = document.createElement('div');\n      footer.className = \"paper-footer\";\n      const footerBrand = document.createElement('span');\n      footerBrand.innerText = \"YMS ENGLISH · BUSONG\";\n      const footerMeta = document.createElement('span');\n      footerMeta.innerText = `${examTb} · UNIT ${examLesson}`;\n      footer.appendChild(footerBrand);\n      footer.appendChild(footerMeta);\n      paper.appendChild(footer);\n    }""",
    "YMS paper footer",
)

path.write_bytes(text.encode("utf-8"))
print("YMS test outline patch applied")
