from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# 1) Sort textbook dropdowns in Korean/natural numeric order.
old = '      const tbKeys = Object.keys(targetMap);\n'
new = '''      const tbKeys = Object.keys(targetMap).sort((a, b) =>
        String(a).localeCompare(String(b), "ko-KR", { numeric: true, sensitivity: "base" })
      );
'''
if old not in text:
    raise SystemExit('main textbook key marker not found')
text = text.replace(old, new, 1)

# 2) Add DB editor UI below the existing word import section.
old = '''      <button id="saveWordsBtn" class="btn-submit" style="background:#0284c7;" onclick="saveWordsToFirebase()">[단어 DB 저장 - 기존 데이터 교체]</button>
    </div>
  </div>

  <script>
'''
new = '''      <button id="saveWordsBtn" class="btn-submit" style="background:#0284c7;" onclick="saveWordsToFirebase()">[단어 DB 저장 - 기존 데이터 교체]</button>

      <hr style="margin:28px 0 20px; border:none; border-top:1px solid #cbd5e1;">

      <!-- DB 조회 / 수정 / 삭제 -->
      <h3>🛠️ 3. 데이터베이스 조회 / 수정 / 삭제</h3>
      <div class="info-tip">
        💡 교과서와 과를 선택하면 저장된 항목을 직접 수정하거나 삭제할 수 있습니다.<br>
        <b>과 전체 삭제</b>는 해당 교과서/과의 데이터가 모두 지워지므로 확인창을 한 번 더 거칩니다.
      </div>

      <div class="row form-group">
        <div class="col">
          <label>데이터 종류</label>
          <select id="dbEditorCategory" onchange="refreshDbEditorFilters()">
            <option value="sentence">문장/지문</option>
            <option value="vocab">단어</option>
          </select>
        </div>
        <div class="col">
          <label>교과서</label>
          <select id="dbEditorTb" onchange="updateDbEditorLessonDropdown()"></select>
        </div>
        <div class="col">
          <label>과</label>
          <select id="dbEditorLesson"></select>
        </div>
      </div>

      <div style="display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
        <button type="button" onclick="loadDbEditor()" style="flex:1; min-width:180px; padding:10px 14px; background:#2563eb; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🔎 선택 데이터 불러오기</button>
        <button type="button" onclick="refreshDbEditorFilters()" style="padding:10px 14px; background:#475569; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🔄 목록 새로고침</button>
        <button type="button" onclick="deleteDbLesson()" style="padding:10px 14px; background:#dc2626; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🗑️ 이 과 전체 삭제</button>
      </div>

      <div id="dbEditorStatus" style="font-size:13px; font-weight:bold; color:#475569; margin:8px 0 12px;">관리자 로그인 후 데이터를 선택해 주세요.</div>
      <div id="dbEditorList"></div>
    </div>
  </div>

  <script>
'''
if old not in text:
    raise SystemExit('admin UI insertion marker not found')
text = text.replace(old, new, 1)

# 3) Track DB editor index and refresh it after admin login.
old = '''    let isPinVerified = false;
    let dbSentenceMap = {};
    let dbWordMap = {};

    auth.onAuthStateChanged(user => {
'''
new = '''    let isPinVerified = false;
    let dbSentenceMap = {};
    let dbWordMap = {};
    let dbEditorIndex = {};

    auth.onAuthStateChanged(user => {
'''
if old not in text:
    raise SystemExit('global state marker not found')
text = text.replace(old, new, 1)

old = '''        document.getElementById('adminSection').style.display = 'block';
        document.getElementById('userEmailText').innerText = user.email;
      } else {
'''
new = '''        document.getElementById('adminSection').style.display = 'block';
        document.getElementById('userEmailText').innerText = user.email;
        refreshDbEditorFilters().catch(err => {
          const status = document.getElementById('dbEditorStatus');
          if (status) status.innerText = "DB 관리 목록 로드 실패: " + err.message;
        });
      } else {
'''
if old not in text:
    raise SystemExit('auth login marker not found')
text = text.replace(old, new, 1)

old = '''        document.getElementById('loginSection').style.display = 'block';
        document.getElementById('adminSection').style.display = 'none';
      }
    });
'''
new = '''        document.getElementById('loginSection').style.display = 'block';
        document.getElementById('adminSection').style.display = 'none';
        dbEditorIndex = {};
        const editorList = document.getElementById('dbEditorList');
        if (editorList) editorList.innerHTML = "";
      }
    });
'''
if old not in text:
    raise SystemExit('auth logout marker not found')
text = text.replace(old, new, 1)

# 4) Add reusable admin DB editor functions before login handler.
marker = '''    function handleLogin() {
'''
insert = r'''    function naturalKoreanCompare(a, b) {
      return String(a ?? "").localeCompare(String(b ?? ""), "ko-KR", {
        numeric: true,
        sensitivity: "base"
      });
    }

    function getEditorCollectionName() {
      return document.getElementById('dbEditorCategory').value === "sentence" ? "sentences" : "words";
    }

    async function refreshDbEditorFilters(preferredTb = "", preferredLesson = "") {
      if (!auth.currentUser) return;

      const category = document.getElementById('dbEditorCategory').value;
      const collectionName = category === "sentence" ? "sentences" : "words";
      const tbSelect = document.getElementById('dbEditorTb');
      const lessonSelect = document.getElementById('dbEditorLesson');
      const status = document.getElementById('dbEditorStatus');

      const currentTb = preferredTb || tbSelect.value;
      const currentLesson = String(preferredLesson || lessonSelect.value || "");

      status.innerText = "DB 목록을 불러오는 중입니다...";
      const snapshot = await db.collection(collectionName).get();
      const index = {};

      snapshot.forEach(doc => {
        const data = doc.data();
        const tb = String(data.tbCode || "").trim();
        const lesson = Number(data.lesson);
        if (!tb || !Number.isFinite(lesson)) return;
        if (!index[tb]) index[tb] = {};
        index[tb][lesson] = (index[tb][lesson] || 0) + 1;
      });

      dbEditorIndex = index;
      tbSelect.innerHTML = "";

      const tbKeys = Object.keys(index).sort(naturalKoreanCompare);
      if (tbKeys.length === 0) {
        tbSelect.innerHTML = "<option value=''>등록된 데이터가 없습니다</option>";
        lessonSelect.innerHTML = "";
        document.getElementById('dbEditorList').innerHTML = "";
        status.innerText = "등록된 데이터가 없습니다.";
        return;
      }

      tbKeys.forEach(tb => {
        const opt = document.createElement('option');
        opt.value = tb;
        opt.innerText = tb;
        tbSelect.appendChild(opt);
      });

      if (currentTb && index[currentTb]) tbSelect.value = currentTb;
      updateDbEditorLessonDropdown(currentLesson);
      status.innerText = "교과서와 과를 선택한 뒤 [선택 데이터 불러오기]를 눌러 주세요.";
    }

    function updateDbEditorLessonDropdown(preferredLesson = "") {
      const tb = document.getElementById('dbEditorTb').value;
      const lessonSelect = document.getElementById('dbEditorLesson');
      const currentLesson = String(preferredLesson || lessonSelect.value || "");
      lessonSelect.innerHTML = "";

      if (!tb || !dbEditorIndex[tb]) return;

      const lessons = Object.keys(dbEditorIndex[tb]).map(Number).sort((a, b) => a - b);
      lessons.forEach(lesson => {
        const opt = document.createElement('option');
        opt.value = lesson;
        opt.innerText = `${lesson}과 (${dbEditorIndex[tb][lesson]}개)`;
        lessonSelect.appendChild(opt);
      });

      if (currentLesson && dbEditorIndex[tb][Number(currentLesson)]) {
        lessonSelect.value = Number(currentLesson);
      }
    }

    function getDocCreatedTime(data) {
      const value = data.createdAt || data.importSavedAt;
      if (!value) return 0;
      if (typeof value.toMillis === "function") return value.toMillis();
      if (typeof value.seconds === "number") return value.seconds * 1000;
      return 0;
    }

    async function getDbEditorDocuments() {
      const collectionName = getEditorCollectionName();
      const tb = document.getElementById('dbEditorTb').value;
      const lesson = Number(document.getElementById('dbEditorLesson').value);
      if (!tb || !Number.isFinite(lesson)) return [];

      const snapshot = await db.collection(collectionName).where("tbCode", "==", tb).get();
      const docs = [];
      snapshot.forEach(doc => {
        const data = doc.data();
        if (Number(data.lesson) !== lesson) return;
        docs.push({ id: doc.id, ref: doc.ref, data });
      });

      docs.sort((a, b) => {
        const aNum = Number(a.data.num);
        const bNum = Number(b.data.num);
        const aValid = Number.isFinite(aNum);
        const bValid = Number.isFinite(bNum);
        if (aValid && bValid && aNum !== bNum) return aNum - bNum;
        if (aValid && !bValid) return -1;
        if (!aValid && bValid) return 1;
        return getDocCreatedTime(a.data) - getDocCreatedTime(b.data);
      });
      return docs;
    }

    function makeEditorInput(field, value, options = {}) {
      const el = options.multiline ? document.createElement('textarea') : document.createElement('input');
      el.dataset.field = field;
      el.value = value ?? "";
      el.style.width = "100%";
      el.style.padding = "8px";
      el.style.border = "1px solid #cbd5e1";
      el.style.borderRadius = "5px";
      el.style.fontFamily = "inherit";
      el.style.fontSize = "13px";
      if (options.multiline) {
        el.rows = options.rows || 2;
        el.style.resize = "vertical";
      } else if (options.type) {
        el.type = options.type;
      }
      return el;
    }

    async function loadDbEditor() {
      if (!auth.currentUser) return alert("관리자 로그인이 필요합니다.");

      const category = document.getElementById('dbEditorCategory').value;
      const collectionName = getEditorCollectionName();
      const tb = document.getElementById('dbEditorTb').value;
      const lesson = Number(document.getElementById('dbEditorLesson').value);
      const list = document.getElementById('dbEditorList');
      const status = document.getElementById('dbEditorStatus');

      if (!tb || !Number.isFinite(lesson)) return alert("교과서와 과를 선택해 주세요.");

      status.innerText = "데이터를 불러오는 중입니다...";
      list.innerHTML = "";

      try {
        const docs = await getDbEditorDocuments();
        if (docs.length === 0) {
          status.innerText = `${tb} ${lesson}과에 저장된 데이터가 없습니다.`;
          return;
        }

        status.innerText = `${tb} ${lesson}과 ${docs.length}개 항목을 불러왔습니다. 수정 후 각 행의 [저장]을 누르세요.`;

        docs.forEach((item, idx) => {
          const card = document.createElement('div');
          card.style.border = "1px solid #dbe3ee";
          card.style.borderRadius = "7px";
          card.style.padding = "10px";
          card.style.marginBottom = "8px";
          card.style.background = idx % 2 === 0 ? "#ffffff" : "#f8fafc";

          const grid = document.createElement('div');
          grid.style.display = "grid";
          grid.style.gridTemplateColumns = category === "sentence" ? "75px 1fr 1fr auto" : "75px 1fr 1fr auto";
          grid.style.gap = "8px";
          grid.style.alignItems = "center";

          grid.appendChild(makeEditorInput("num", item.data.num ?? "", { type: "number" }));
          if (category === "sentence") {
            grid.appendChild(makeEditorInput("eng", item.data.eng || "", { multiline: true, rows: 2 }));
            grid.appendChild(makeEditorInput("kor", item.data.kor || "", { multiline: true, rows: 2 }));
          } else {
            grid.appendChild(makeEditorInput("word", item.data.word || ""));
            grid.appendChild(makeEditorInput("meaning", item.data.meaning || ""));
          }

          const buttons = document.createElement('div');
          buttons.style.display = "flex";
          buttons.style.gap = "6px";

          const saveBtn = document.createElement('button');
          saveBtn.type = "button";
          saveBtn.innerText = "저장";
          saveBtn.style.cssText = "padding:8px 10px;background:#059669;color:white;border:none;border-radius:5px;font-weight:bold;cursor:pointer;";
          saveBtn.onclick = () => saveDbRecord(collectionName, item.id, card);

          const deleteBtn = document.createElement('button');
          deleteBtn.type = "button";
          deleteBtn.innerText = "삭제";
          deleteBtn.style.cssText = "padding:8px 10px;background:#dc2626;color:white;border:none;border-radius:5px;font-weight:bold;cursor:pointer;";
          deleteBtn.onclick = () => deleteDbRecord(collectionName, item.id, item.data);

          buttons.appendChild(saveBtn);
          buttons.appendChild(deleteBtn);
          grid.appendChild(buttons);
          card.appendChild(grid);
          list.appendChild(card);
        });
      } catch (err) {
        status.innerText = "DB 데이터 로드 실패: " + err.message;
      }
    }

    async function saveDbRecord(collectionName, docId, card) {
      const category = document.getElementById('dbEditorCategory').value;
      const numValue = Number(card.querySelector('[data-field="num"]').value);
      if (!Number.isFinite(numValue) || numValue < 1) return alert("번호는 1 이상의 숫자로 입력해 주세요.");

      const payload = { num: numValue };
      if (category === "sentence") {
        payload.eng = card.querySelector('[data-field="eng"]').value.trim();
        payload.kor = card.querySelector('[data-field="kor"]').value.trim();
        if (!payload.eng || !payload.kor) return alert("영어 문장과 한글 해석을 모두 입력해 주세요.");
      } else {
        payload.word = card.querySelector('[data-field="word"]').value.trim();
        payload.meaning = card.querySelector('[data-field="meaning"]').value.trim();
        if (!payload.word || !payload.meaning) return alert("영단어와 뜻을 모두 입력해 주세요.");
      }

      try {
        await db.collection(collectionName).doc(docId).update(payload);
        card.style.borderColor = "#16a34a";
        document.getElementById('dbEditorStatus').innerText = "✅ 수정 내용을 저장했습니다.";
        await loadDropdownsFromDB();
      } catch (err) {
        alert("수정 저장 실패: " + err.message);
      }
    }

    async function deleteDbRecord(collectionName, docId, data) {
      const label = data.eng || data.word || `번호 ${data.num ?? ""}`;
      if (!confirm(`정말 이 항목을 삭제할까요?\n\n${label}`)) return;

      const tb = document.getElementById('dbEditorTb').value;
      const lesson = document.getElementById('dbEditorLesson').value;

      try {
        await db.collection(collectionName).doc(docId).delete();
        await loadDropdownsFromDB();
        await refreshDbEditorFilters(tb, lesson);
        await loadDbEditor();
      } catch (err) {
        alert("삭제 실패: " + err.message);
      }
    }

    async function deleteDbLesson() {
      if (!auth.currentUser) return alert("관리자 로그인이 필요합니다.");

      const category = document.getElementById('dbEditorCategory').value;
      const collectionName = getEditorCollectionName();
      const tb = document.getElementById('dbEditorTb').value;
      const lesson = Number(document.getElementById('dbEditorLesson').value);
      if (!tb || !Number.isFinite(lesson)) return alert("교과서와 과를 선택해 주세요.");

      let docs;
      try {
        docs = await getDbEditorDocuments();
      } catch (err) {
        return alert("삭제할 데이터 확인 실패: " + err.message);
      }

      if (docs.length === 0) return alert("삭제할 데이터가 없습니다.");

      const typeLabel = category === "sentence" ? "문장/지문" : "단어";
      if (!confirm(`⚠️ ${tb} ${lesson}과의 ${typeLabel} ${docs.length}개를 모두 삭제할까요?\n\n이 작업은 되돌릴 수 없습니다.`)) return;

      try {
        const chunkSize = 400;
        for (let offset = 0; offset < docs.length; offset += chunkSize) {
          const batch = db.batch();
          docs.slice(offset, offset + chunkSize).forEach(item => batch.delete(item.ref));
          await batch.commit();
        }

        document.getElementById('dbEditorList').innerHTML = "";
        document.getElementById('dbEditorStatus').innerText = `✅ ${tb} ${lesson}과 ${typeLabel} ${docs.length}개를 삭제했습니다.`;
        await loadDropdownsFromDB();
        await refreshDbEditorFilters(tb, "");
      } catch (err) {
        alert("과 전체 삭제 실패: " + err.message);
      }
    }

'''
if marker not in text:
    raise SystemExit('login handler marker not found')
text = text.replace(marker, insert + marker, 1)

# 5) Refresh editor filter list after successful sentence/word saves.
old = '''        alert(`총 ${engList.length}개 문장이 성공적으로 DB에 저장되었습니다!`);
        document.getElementById('dbStartNum').value = startNum + engList.length;
'''
new = '''        alert(`총 ${engList.length}개 문장이 성공적으로 DB에 저장되었습니다!`);
        refreshDbEditorFilters(tb, lesson).catch(() => {});
        document.getElementById('dbStartNum').value = startNum + engList.length;
'''
if old not in text:
    raise SystemExit('sentence save success marker not found')
text = text.replace(old, new, 1)

old = '''        // 화면 데이터도 DB에서 다시 불러오기
        await loadDropdownsFromDB();

        const duplicateRemoved = parsed.length - uniqueParsed.length;
'''
new = '''        // 화면 데이터도 DB에서 다시 불러오기
        await loadDropdownsFromDB();
        await refreshDbEditorFilters(tb, lesson);

        const duplicateRemoved = parsed.length - uniqueParsed.length;
'''
if old not in text:
    raise SystemExit('word save refresh marker not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8', newline='\r\n')
