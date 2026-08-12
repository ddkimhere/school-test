from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = '''    function updateLessonDropdown() {
      const category = document.getElementById('genCategory').value;
      const targetMap = (category === "sentence") ? dbSentenceMap : dbWordMap;
      const genTbSelect = document.getElementById('genTb');
      const genTypeSelect = document.getElementById('genType');
      
      genTbSelect.innerHTML = "";
'''
new = '''    function updateLessonDropdown() {
      const category = document.getElementById('genCategory').value;
      const targetMap = (category === "sentence") ? dbSentenceMap : dbWordMap;
      const genTbSelect = document.getElementById('genTb');
      const genLessonSelect = document.getElementById('genLesson');
      const genTypeSelect = document.getElementById('genType');
      const previousTb = genTbSelect.value;
      const previousLesson = genLessonSelect.value;
      
      genTbSelect.innerHTML = "";
'''
if old not in text:
    raise SystemExit('updateLessonDropdown header not found')
text = text.replace(old, new, 1)

old = '''      const selectedTb = genTbSelect.value;
      const genLessonSelect = document.getElementById('genLesson');
      genLessonSelect.innerHTML = "";

      if (selectedTb && targetMap[selectedTb]) {
        const lessons = Object.keys(targetMap[selectedTb]).map(Number).sort((a, b) => a - b);
        lessons.forEach(l => {
          const opt = document.createElement('option');
          opt.value = l;
          opt.innerText = `${l}과`;
          genLessonSelect.appendChild(opt);
        });
      }

      updateRangeDropdowns();
'''
new = '''      if (previousTb && targetMap[previousTb]) {
        genTbSelect.value = previousTb;
      }

      const selectedTb = genTbSelect.value;
      genLessonSelect.innerHTML = "";

      if (selectedTb && targetMap[selectedTb]) {
        const lessons = Object.keys(targetMap[selectedTb]).map(Number).sort((a, b) => a - b);
        lessons.forEach(l => {
          const opt = document.createElement('option');
          opt.value = l;
          const count = Array.isArray(targetMap[selectedTb][l]) ? targetMap[selectedTb][l].length : 0;
          opt.innerText = `${l}과 (${count}개)`;
          genLessonSelect.appendChild(opt);
        });

        if (previousLesson && targetMap[selectedTb][previousLesson]) {
          genLessonSelect.value = previousLesson;
        }
      }

      updateRangeDropdowns();
'''
if old not in text:
    raise SystemExit('updateLessonDropdown body not found')
text = text.replace(old, new, 1)

marker = '''    function getWordTimestamp(item) {
      if (!item.createdAt) return 0;
      if (typeof item.createdAt.toMillis === "function") return item.createdAt.toMillis();
      if (typeof item.createdAt.seconds === "number") return item.createdAt.seconds * 1000;
      return 0;
    }

'''
insert = '''    function getLatestImportedWordItems(allItems) {
      if (!Array.isArray(allItems) || allItems.length === 0) return [];

      const importedItems = allItems.filter(item => item.importId);
      if (importedItems.length === 0) return allItems;

      const importTimeMap = {};
      importedItems.forEach(item => {
        let t = 0;
        if (item.importSavedAt) {
          if (typeof item.importSavedAt.toMillis === "function") {
            t = item.importSavedAt.toMillis();
          } else if (typeof item.importSavedAt.seconds === "number") {
            t = item.importSavedAt.seconds * 1000;
          }
        }
        if (!t && typeof item.importId === "string") {
          const match = item.importId.match(/^(\\d+)_/);
          if (match) t = Number(match[1]);
        }
        if (!importTimeMap[item.importId] || t > importTimeMap[item.importId]) {
          importTimeMap[item.importId] = t;
        }
      });

      const latestImportId = Object.keys(importTimeMap)
        .sort((a, b) => importTimeMap[b] - importTimeMap[a])[0];

      return importedItems.filter(item => item.importId === latestImportId);
    }

    async function fetchLatestWordsFromDB(tb, lesson) {
      const snapshot = await db.collection("words").where("tbCode", "==", tb).get();
      const items = [];

      snapshot.forEach(doc => {
        const data = doc.data();
        if (Number(data.lesson) !== Number(lesson)) return;
        items.push({
          word: data.word,
          meaning: data.meaning,
          num: data.num ?? null,
          createdAt: data.createdAt ?? null,
          importId: data.importId ?? null,
          importSavedAt: data.importSavedAt ?? null
        });
      });

      return getLatestImportedWordItems(items);
    }

'''
if marker not in text:
    raise SystemExit('word timestamp marker not found')
text = text.replace(marker, marker + insert, 1)

text = text.replace('    function fetchAndGenerate() {', '    async function fetchAndGenerate() {', 1)

old = '''        const availableList = getSortedWords(tb, lesson)
          .filter(item => item.displayNum >= start && item.displayNum <= end);

        if (availableList.length === 0) {
          return alert("선택한 범위에 단어가 없습니다.");
        }
'''
new = '''        let latestWords;
        try {
          latestWords = await fetchLatestWordsFromDB(tb, lesson);
        } catch (err) {
          return alert("단어 DB를 새로 불러오지 못했습니다: " + err.message);
        }

        if (!latestWords || latestWords.length === 0) {
          return alert(`${tb} ${lesson}과에 저장된 단어를 찾지 못했습니다. DB 관리에서 교과서 코드와 과 번호를 확인해 주세요.`);
        }

        if (!dbWordMap[tb]) dbWordMap[tb] = {};
        dbWordMap[tb][lesson] = latestWords;

        const availableList = getSortedWords(tb, lesson)
          .filter(item => item.displayNum >= start && item.displayNum <= end);

        if (availableList.length === 0) {
          const allWords = getSortedWords(tb, lesson);
          const minNum = allWords.length ? allWords[0].displayNum : 1;
          const maxNum = allWords.length ? allWords[allWords.length - 1].displayNum : 1;
          return alert(`선택한 ${start}~${end}번 범위에는 단어가 없습니다. ${lesson}과의 현재 단어 번호 범위는 ${minNum}~${maxNum}번입니다.`);
        }
'''
if old not in text:
    raise SystemExit('vocab generation block not found')
text = text.replace(old, new, 1)

old = '''      <button class="btn-submit" onclick="fetchAndGenerate()">문제지 만들기</button>
    </div>
'''
new = '''      <div style="display:flex; gap:10px;">
        <button class="btn-submit" onclick="fetchAndGenerate()" style="flex:1;">문제지 만들기</button>
        <button type="button" onclick="loadDropdownsFromDB()" style="width:180px; background:#475569; color:white; font-weight:bold; border:none; border-radius:6px; cursor:pointer;">🔄 DB 목록 새로고침</button>
      </div>
    </div>
'''
if old not in text:
    raise SystemExit('generate button block not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('patched index.html')
