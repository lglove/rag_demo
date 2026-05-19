from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>企业知识库问答 Demo</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --line: #d9dee7;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --danger: #dc2626;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }

    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    .topbar {
      max-width: 1180px;
      margin: 0 auto;
      padding: 18px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 700;
    }

    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: 380px minmax(0, 1fr);
      gap: 20px;
    }

    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }

    h2 {
      margin: 0 0 14px;
      font-size: 15px;
    }

    label {
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 13px;
    }

    input[type="file"],
    input[type="number"],
    textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
      padding: 9px 10px;
      font: inherit;
    }

    textarea {
      min-height: 96px;
      resize: vertical;
    }

    button {
      border: 0;
      border-radius: 6px;
      background: var(--primary);
      color: white;
      padding: 9px 12px;
      font: inherit;
      cursor: pointer;
    }

    button:hover {
      background: var(--primary-dark);
    }

    button.secondary {
      background: #eef2ff;
      color: #1e40af;
    }

    button.secondary:hover {
      background: #dbe4ff;
    }

    button.danger {
      background: #fee2e2;
      color: var(--danger);
    }

    button.danger:hover {
      background: #fecaca;
    }

    .stack {
      display: grid;
      gap: 14px;
    }

    .row {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }

    .document-list {
      display: grid;
      gap: 10px;
      max-height: 420px;
      overflow: auto;
    }

    .document {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      display: grid;
      gap: 8px;
    }

    .document-main {
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }

    .document-title {
      font-weight: 650;
      word-break: break-all;
    }

    .meta {
      color: var(--muted);
      font-size: 12px;
      word-break: break-all;
    }

    .answer {
      min-height: 120px;
      white-space: pre-wrap;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcff;
    }

    .source {
      border-left: 3px solid var(--primary);
      background: #f8fafc;
      padding: 10px 12px;
      margin-top: 10px;
      border-radius: 6px;
    }

    .source-content {
      margin-top: 6px;
      white-space: pre-wrap;
    }

    .status {
      color: var(--muted);
      font-size: 13px;
    }

    @media (max-width: 860px) {
      main {
        grid-template-columns: 1fr;
        padding: 16px;
      }

      .topbar {
        padding: 16px;
        align-items: flex-start;
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <h1>企业知识库问答 Demo</h1>
      <a href="/docs" target="_blank">API Docs</a>
    </div>
  </header>

  <main>
    <div class="stack">
      <section>
        <h2>上传文档</h2>
        <div class="stack">
          <div>
            <label for="uploadFile">支持 txt / md</label>
            <input id="uploadFile" type="file" accept=".txt,.md" />
          </div>
          <button onclick="uploadDocument()">上传</button>
          <div id="uploadStatus" class="status"></div>
        </div>
      </section>

      <section>
        <div class="row" style="justify-content: space-between;">
          <h2>文档列表</h2>
          <button class="secondary" onclick="loadDocuments()">刷新</button>
        </div>
        <div id="documents" class="document-list"></div>
      </section>
    </div>

    <div class="stack">
      <section>
        <h2>提问</h2>
        <div class="stack">
          <div>
            <label for="question">问题</label>
            <textarea id="question" placeholder="例如：公司年假制度是怎样的？"></textarea>
          </div>
          <div class="row">
            <div style="width: 120px;">
              <label for="topK">Top-K</label>
              <input id="topK" type="number" min="1" max="20" value="5" />
            </div>
            <button onclick="askQuestion()">提问</button>
            <span class="status">勾选文档后只在选中文档中检索</span>
          </div>
        </div>
      </section>

      <section>
        <h2>答案</h2>
        <div id="answer" class="answer">等待提问。</div>
      </section>

      <section>
        <h2>引用来源</h2>
        <div id="sources" class="status">暂无引用。</div>
      </section>
    </div>
  </main>

  <script>
    async function requestJson(url, options) {
      const response = await fetch(url, options);
      const text = await response.text();
      let data = null;
      try {
        data = text ? JSON.parse(text) : null;
      } catch (error) {
        data = { detail: text };
      }
      if (!response.ok) {
        const message = data && data.detail ? data.detail : "请求失败";
        throw new Error(Array.isArray(message) ? JSON.stringify(message) : message);
      }
      return data;
    }

    async function uploadDocument() {
      const input = document.getElementById("uploadFile");
      const status = document.getElementById("uploadStatus");
      if (!input.files.length) {
        status.textContent = "请选择文件。";
        return;
      }

      const form = new FormData();
      form.append("file", input.files[0]);
      status.textContent = "上传中...";

      try {
        const data = await requestJson("/upload", { method: "POST", body: form });
        status.textContent = `上传完成：${data.filename}，chunks=${data.chunk_count}`;
        input.value = "";
        await loadDocuments();
      } catch (error) {
        status.textContent = error.message;
      }
    }

    async function updateDocument(documentId) {
      const input = document.getElementById(`update-${documentId}`);
      if (!input.files.length) {
        alert("请选择更新文件。");
        return;
      }

      const form = new FormData();
      form.append("file", input.files[0]);

      try {
        const data = await requestJson(`/documents/${documentId}`, {
          method: "PUT",
          body: form,
        });
        alert(`更新完成：active_version=${data.active_version}`);
        await loadDocuments();
      } catch (error) {
        alert(error.message);
      }
    }

    async function deleteDocument(documentId) {
      if (!confirm("确认删除这个文档？")) {
        return;
      }

      try {
        await requestJson(`/documents/${documentId}`, { method: "DELETE" });
        await loadDocuments();
      } catch (error) {
        alert(error.message);
      }
    }

    async function loadDocuments() {
      const container = document.getElementById("documents");
      container.innerHTML = '<div class="status">加载中...</div>';

      try {
        const documents = await requestJson("/documents");
        if (!documents.length) {
          container.innerHTML = '<div class="status">暂无文档。</div>';
          return;
        }

        container.innerHTML = documents.map((doc) => `
          <div class="document">
            <div class="document-main">
              <input type="checkbox" class="doc-check" value="${doc.document_id}" />
              <div>
                <div class="document-title">${escapeHtml(doc.filename)}</div>
                <div class="meta">${doc.document_id}</div>
                <div class="meta">chunks=${doc.chunk_count} · version=${doc.active_version} · ${doc.status}</div>
              </div>
            </div>
            <div class="row">
              <input id="update-${doc.document_id}" type="file" accept=".txt,.md" />
              <button class="secondary" onclick="updateDocument('${doc.document_id}')">更新</button>
              <button class="danger" onclick="deleteDocument('${doc.document_id}')">删除</button>
            </div>
          </div>
        `).join("");
      } catch (error) {
        container.innerHTML = `<div class="status">${escapeHtml(error.message)}</div>`;
      }
    }

    async function askQuestion() {
      const answer = document.getElementById("answer");
      const sources = document.getElementById("sources");
      const question = document.getElementById("question").value.trim();
      const topK = Number(document.getElementById("topK").value || 5);
      const selected = Array.from(document.querySelectorAll(".doc-check:checked"))
        .map((item) => item.value);

      if (!question) {
        answer.textContent = "请输入问题。";
        return;
      }

      answer.textContent = "生成中...";
      sources.textContent = "检索中...";

      const payload = { question, top_k: topK };
      if (selected.length) {
        payload.document_ids = selected;
      }

      try {
        const data = await requestJson("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        answer.textContent = data.answer;
        renderSources(data.sources || []);
      } catch (error) {
        answer.textContent = error.message;
        sources.textContent = "暂无引用。";
      }
    }

    function renderSources(items) {
      const container = document.getElementById("sources");
      if (!items.length) {
        container.textContent = "暂无引用。";
        return;
      }

      container.innerHTML = items.map((source) => `
        <div class="source">
          <div><strong>${escapeHtml(source.document)}</strong> · chunk ${source.chunk_id} · score ${source.score}</div>
          <div class="meta">${source.document_id}</div>
          <div class="source-content">${escapeHtml(source.content)}</div>
        </div>
      `).join("");
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    loadDocuments();
  </script>
</body>
</html>
"""
