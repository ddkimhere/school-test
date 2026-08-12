from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_buttons = '''      <div style="display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
        <button type="button" onclick="loadDbEditor()" style="flex:1; min-width:180px; padding:10px 14px; background:#2563eb; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🔎 선택 데이터 불러오기</button>
        <button type="button" onclick="refreshDbEditorFilters()" style="padding:10px 14px; background:#475569; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🔄 목록 새로고침</button>
        <button type="button" onclick="deleteDbLesson()" style="padding:10px 14px; background:#dc2626; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🗑️ 이 과 전체 삭제</button>
      </div>
'''

new_buttons = '''      <div style="display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
        <button type="button" onclick="loadDbEditor()" style="flex:1; min-width:180px; padding:10px 14px; background:#2563eb; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🔎 선택 데이터 불러오기</button>
        <button type="button" onclick="refreshDbEditorFilters()" style="padding:10px 14px; background:#475569; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🔄 목록 새로고침</button>
        <button type="button" onclick="renameDbTextbook()" style="padding:10px 14px; background:#7c3aed; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">✏️ 교과서 이름 변경</button>
        <button type="button" onclick="deleteDbLesson()" style="padding:10px 14px; background:#dc2626; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">🗑️ 이 과 전체 삭제</button>
      </div>
'''

if old_buttons not in text:
    raise SystemExit('DB editor button block not found')
text = text.replace(old_buttons, new_buttons, 1)

marker = '''    async function deleteDbLesson() {
'''

rename_function = r'''    async function renameDbTextbook() {
      if (!auth.currentUser) return alert("관리자 로그인이 필요합니다.");

      const oldTb = document.getElementById('dbEditorTb').value;
      const currentLesson = document.getElementById('dbEditorLesson').value;
      if (!oldTb) return alert("변경할 교과서를 선택해 주세요.");

      const entered = prompt(
        `교과서 이름을 변경합니다.\n\n현재 이름: ${oldTb}\n새 이름을 입력해 주세요.`,
        oldTb
      );
      if (entered === null) return;

      const newTb = entered.trim();
      if (!newTb) return alert("새 교과서 이름을 입력해 주세요.");
      if (newTb === oldTb) return alert("현재 이름과 같습니다.");

      const collections = ["sentences", "words"];
      const sourceDocs = [];
      let targetCount = 0;

      try {
        for (const collectionName of collections) {
          const sourceSnapshot = await db.collection(collectionName).where("tbCode", "==", oldTb).get();
          sourceSnapshot.forEach(doc => sourceDocs.push({ collectionName, ref: doc.ref }));

          const targetSnapshot = await db.collection(collectionName).where("tbCode", "==", newTb).get();
          targetCount += targetSnapshot.size;
        }
      } catch (err) {
        return alert("교과서 데이터 확인 실패: " + err.message);
      }

      if (sourceDocs.length === 0) {
        return alert(`${oldTb} 이름으로 저장된 데이터를 찾지 못했습니다.`);
      }

      if (targetCount > 0) {
        const mergeOk = confirm(
          `⚠️ '${newTb}' 이름으로 이미 ${targetCount}개 데이터가 있습니다.\n\n` +
          `이름을 변경하면 기존 '${newTb}' 데이터와 같은 교과서 이름으로 합쳐져 보입니다.\n` +
          `그래도 계속할까요?`
        );
        if (!mergeOk) return;
      }

      const finalOk = confirm(
        `교과서 이름을 변경할까요?\n\n` +
        `${oldTb} → ${newTb}\n\n` +
        `문장/지문과 단어 DB의 모든 과를 포함해 총 ${sourceDocs.length}개 데이터의 교과서 이름이 함께 변경됩니다.`
      );
      if (!finalOk) return;

      try {
        const chunkSize = 400;
        for (let offset = 0; offset < sourceDocs.length; offset += chunkSize) {
          const batch = db.batch();
          sourceDocs.slice(offset, offset + chunkSize).forEach(item => {
            batch.update(item.ref, { tbCode: newTb });
          });
          await batch.commit();
        }

        if (document.getElementById('dbTb').value.trim() === oldTb) {
          document.getElementById('dbTb').value = newTb;
        }
        if (document.getElementById('dbWordTb').value.trim() === oldTb) {
          document.getElementById('dbWordTb').value = newTb;
        }

        document.getElementById('dbEditorStatus').innerText = `✅ 교과서 이름을 '${oldTb}'에서 '${newTb}'로 변경했습니다.`;
        await loadDropdownsFromDB();
        await refreshDbEditorFilters(newTb, currentLesson);
        await loadDbEditor();
      } catch (err) {
        alert("교과서 이름 변경 실패: " + err.message);
      }
    }

'''

if marker not in text:
    raise SystemExit('deleteDbLesson marker not found')
text = text.replace(marker, rename_function + marker, 1)

path.write_text(text, encoding='utf-8')
