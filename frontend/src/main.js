import "./style.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const conversation = document.querySelector("#conversation");
const status = document.querySelector("#status");
const ingestButton = document.querySelector("#ingest-button");

function addMessage(role, text, sources = []) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "AI";

  const content = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  content.appendChild(bubble);

  if (sources.length) {
    const sourceList = document.createElement("div");
    sourceList.className = "source-list";
    for (const source of sources) {
      const item = document.createElement("span");
      item.textContent = `${source.document} · page ${source.page}`;
      item.title = source.path;
      sourceList.appendChild(item);
    }
    content.appendChild(sourceList);
  }

  article.append(avatar, content);
  conversation.appendChild(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
  return article;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "The request failed.");
  return data;
}

async function checkHealth() {
  try {
    const data = await apiRequest("/health");
    status.textContent = `${data.indexed_chunks} chunks ready`;
    status.className = data.indexed_chunks ? "status ready" : "status warning";
  } catch {
    status.textContent = "API offline";
    status.className = "status warning";
  }
}

ingestButton.addEventListener("click", async () => {
  ingestButton.disabled = true;
  ingestButton.textContent = "Indexing…";
  try {
    const result = await apiRequest("/ingest", { method: "POST" });
    addMessage(
      "assistant",
      `Index ready: ${result.documents} documents, ${result.pages} pages, ${result.chunks} chunks.`,
    );
    await checkHealth();
  } catch (error) {
    addMessage("assistant", `Indexing failed: ${error.message}`);
  } finally {
    ingestButton.disabled = false;
    ingestButton.textContent = "Index documents";
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  addMessage("user", question);
  input.value = "";
  input.disabled = true;
  const pending = addMessage("assistant", "Searching the approved documents…");

  try {
    const result = await apiRequest("/chat", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
    pending.remove();
    addMessage("assistant", result.answer, result.sources);
  } catch (error) {
    pending.remove();
    addMessage("assistant", `I could not answer: ${error.message}`);
  } finally {
    input.disabled = false;
    input.focus();
  }
});

document.querySelectorAll(".suggestions button").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.textContent;
    input.focus();
  });
});

checkHealth();
