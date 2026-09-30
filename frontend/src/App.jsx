import React, { useEffect, useRef, useState } from "react";
import {
  ArrowUp, Bot, Check, ChevronRight, CircleAlert, Database, FileCheck2,
  FileQuestion, FileText, HelpCircle, LoaderCircle, Menu, PackageCheck,
  RefreshCw, Search, ShieldCheck, Sparkles, Truck, UserRound, Wrench, X,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const documents = [
  ["Return Policy", "5 pages", PackageCheck, "blue"],
  ["Warranty Policy", "5 pages", ShieldCheck, "green"],
  ["Delivery Guide", "5 pages", Truck, "amber"],
  ["Product Manuals", "2 manuals", Wrench, "purple"],
  ["Customer FAQ", "Common questions", HelpCircle, "cyan"],
];
const suggestions = [
  ["Returns", "Can I return a blender after 14 days?", PackageCheck],
  ["Delivery", "How long does delivery take in Kigali?", Truck],
  ["Warranty", "How do I claim a warranty?", ShieldCheck],
  ["Instructions", "How should I clean the SmartBlend 500?", Wrench],
];
const ragSteps = [
  ["Question received", "The customer’s message is sent securely to the FastAPI backend."],
  ["Query embedded", "Gemini converts the question into a 768-dimensional meaning vector."],
  ["ChromaDB searched", "The vector database compares the question with all document chunks."],
  ["Evidence retrieved", "The four best unique pages are selected with their source metadata."],
  ["Prompt augmented", "The question and retrieved evidence are combined into a controlled prompt."],
  ["Answer verified", "Gemini writes from the evidence; document names and page citations are checked."],
];
const welcome = {
  id: "welcome", role: "assistant", sources: [],
  text: "Hello! I search Kigali HomeTech’s approved documents to answer questions about returns, warranties, delivery, payments, and product instructions.",
};

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" }, ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "The request failed.");
  return data;
}

function Brand() {
  return <div className="brand"><div className="brand-mark"><b>K</b><b>H</b></div><div><strong>Kigali HomeTech</strong><span>Knowledge assistant</span></div></div>;
}

function Status({ health }) {
  const map = {
    loading: [LoaderCircle, "Checking system"], online: [Check, `${health.chunks} chunks ready`],
    empty: [CircleAlert, "Index required"], offline: [CircleAlert, "API offline"],
  };
  const [Icon, label] = map[health.state];
  return <div className={`status ${health.state}`}><Icon size={14} className={health.state === "loading" ? "spin" : ""}/><span>{label}</span></div>;
}

function Sidebar({ health, indexing, onIndex, open, onClose }) {
  return <aside className={`sidebar ${open ? "open" : ""}`}>
    <div className="sidebar-top"><Brand/><button className="icon-button mobile-close" onClick={onClose}><X size={18}/></button></div>
    <div className="library-title"><span>Approved library</span><em>6 files</em></div>
    <nav className="document-list">
      {documents.map(([name, meta, Icon, tone]) => <div className="document" key={name}>
        <div className={`doc-icon ${tone}`}><Icon size={17}/></div><div><strong>{name}</strong><span>{meta}</span></div><FileCheck2 size={15}/>
      </div>)}
    </nav>
    <div className="sidebar-spacer"/>
    <section className="index-card">
      <div className="index-head"><div><Database size={18}/></div><p><strong>Knowledge index</strong><span>Local ChromaDB</span></p></div>
      <div className="index-stats"><p><b>{health.chunks || "—"}</b><span>Chunks</span></p><p><b>768</b><span>Dimensions</span></p></div>
      <button onClick={onIndex} disabled={indexing}><RefreshCw size={14} className={indexing ? "spin" : ""}/>{indexing ? "Rebuilding…" : "Rebuild document index"}</button>
    </section>
    <small className="secure-note"><ShieldCheck size={13}/> Approved documents only</small>
  </aside>;
}

function Welcome({ onSelect }) {
  return <section className="welcome">
    <div className="visual"><i/><i/><div><Bot size={28}/></div><FileText className="v-one"/><Database className="v-two"/><Search className="v-three"/></div>
    <span className="kicker"><Sparkles size={14}/> Grounded business answers</span>
    <h1>What can I help you find?</h1>
    <p>Ask naturally. I’ll search the approved Kigali HomeTech documents, explain the answer clearly, and show the exact sources.</p>
    <div className="suggestions">{suggestions.map(([label, question, Icon]) => <button key={label} onClick={() => onSelect(question)}>
      <span><Icon size={17}/></span><p><small>{label}</small><strong>{question}</strong></p><ChevronRight size={16}/>
    </button>)}</div>
  </section>;
}

function Sources({ sources }) {
  return sources?.length ? <div className="source-chips">{sources.map((source, i) => <span key={`${source.path}-${source.page}-${i}`}><FileText size={12}/>{source.document} · p.{source.page}</span>)}</div> : null;
}

function Message({ message }) {
  const user = message.role === "user";
  return <article className={`message ${message.role}`}>
    <div className="avatar">{user ? <UserRound size={17}/> : <Bot size={18}/>}</div>
    <div className="message-content"><div className="message-meta"><strong>{user ? "You" : "HomeTech Assistant"}</strong><span>Now</span></div>
      <div className={`bubble ${message.pending ? "pending" : ""}`}>{message.pending ? <><i/><i/><i/><em>Searching approved documents</em></> : message.text}</div>
      <Sources sources={message.sources}/>
    </div>
  </article>;
}

function TraceDetail({ step, trace }) {
  if (!trace) return <div className="trace-empty">Ask a question first. Then select any step to inspect the real data used for that answer.</div>;
  if (step === 0) return <div className="trace-detail"><span className="trace-label">Actual customer query</span><blockquote>{trace.question.text}</blockquote><small>{trace.question.characters} characters sent to FastAPI</small></div>;
  if (step === 1) return <div className="trace-detail"><div className="trace-facts"><p><span>Model</span><strong>{trace.embedding.model}</strong></p><p><span>Dimensions</span><strong>{trace.embedding.dimensions}</strong></p></div><span className="trace-label">First 8 vector values</span><div className="vector-preview">{trace.embedding.preview.map((value, i) => <code key={i}>{value}</code>)}</div><small>The full vector contains {trace.embedding.dimensions} numbers.</small></div>;
  if (step === 2) return <div className="trace-detail"><div className="trace-facts"><p><span>Database</span><strong>{trace.search.database}</strong></p><p><span>Metric</span><strong>{trace.search.metric}</strong></p><p><span>Chunks searched</span><strong>{trace.search.indexed_chunks}</strong></p><p><span>Candidates</span><strong>{trace.search.candidates_returned}</strong></p></div><span className="trace-label">Collection</span><code className="code-line">{trace.search.collection}</code></div>;
  if (step === 3) return <div className="trace-detail"><span className="trace-label">Actual evidence selected</span><div className="trace-evidence">{trace.retrieval.evidence.map((item) => <article key={item.reference}><strong>{item.document} · page {item.page}</strong><small>{Math.round(item.similarity * 100)}% similarity</small><p>{item.snippet}</p></article>)}</div></div>;
  if (step === 4) return <div className="trace-detail"><div className="trace-facts"><p><span>Question added</span><strong>{trace.augmentation.question_added ? "Yes" : "No"}</strong></p><p><span>Evidence blocks</span><strong>{trace.augmentation.evidence_blocks_added}</strong></p></div><span className="trace-label">Controlled instruction</span><p className="instruction-box">{trace.augmentation.instruction}</p><span className="trace-label">Prompt preview</span><pre>{trace.augmentation.prompt_preview}</pre></div>;
  return <div className="trace-detail"><div className="trace-facts"><p><span>Generation model</span><strong>{trace.generation.model}</strong></p><p><span>Temperature</span><strong>{trace.generation.temperature}</strong></p><p><span>Citations checked</span><strong>{trace.generation.citations_verified}</strong></p></div><span className="trace-label">Verified response</span><p className="answer-preview">{trace.generation.answer}</p></div>;
}

function Evidence({ sources, trace }) {
  const [activeStep, setActiveStep] = useState(0);
  const complete = Boolean(trace);
  useEffect(() => { setActiveStep(0); }, [trace?.question?.text]);
  return <aside className="evidence">
    <div className="evidence-title"><div><span>Transparency</span><h2>Answer evidence</h2></div><ShieldCheck size={19}/></div>
    {sources.length ? <div className="evidence-list">{sources.map((source, i) => <article key={`${source.path}-${source.page}-${i}`}>
      <b>{String(i + 1).padStart(2, "0")}</b><div><strong>{source.document}</strong><span><FileText size={12}/>Page {source.page}</span><div className="score"><i><u style={{width: `${Math.round(source.similarity * 100)}%`}}/></i><small>{Math.round(source.similarity * 100)}% match</small></div></div>
    </article>)}</div> : <div className="evidence-empty"><div><FileQuestion size={25}/></div><strong>Sources will appear here</strong><p>Ask a question to see which approved pages support the answer.</p></div>}
    <section className={`process ${complete ? "complete" : ""}`}>
      <div className="process-heading"><span>Query to response</span><small>{complete ? "Completed" : "Process preview"}</small></div>
      {ragSteps.map(([title, detail], i) => <button type="button" className={`process-step ${activeStep === i ? "active" : ""}`} key={title} onClick={() => setActiveStep(i)} aria-expanded={activeStep === i}>
        <div className="step-marker">{complete ? <Check size={11}/> : i + 1}</div>
        <div className="step-copy"><strong>{title}</strong><p>{detail}</p></div>
        {i < ragSteps.length - 1 && <i/>}
      </button>)}
      <TraceDetail step={activeStep} trace={trace}/>
    </section>
  </aside>;
}

export default function App() {
  const [messages, setMessages] = useState([welcome]);
  const [question, setQuestion] = useState("");
  const [health, setHealth] = useState({ state: "loading", chunks: 0 });
  const [asking, setAsking] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [menu, setMenu] = useState(false);
  const end = useRef(null);
  const input = useRef(null);
  const latestAnswer = [...messages].reverse().find((item) => item.trace);
  const latestSources = latestAnswer?.sources || [];
  const latestTrace = latestAnswer?.trace || null;

  useEffect(() => { checkHealth(); }, []);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function checkHealth() {
    try { const data = await request("/health"); setHealth({ state: data.indexed_chunks ? "online" : "empty", chunks: data.indexed_chunks }); }
    catch { setHealth({ state: "offline", chunks: 0 }); }
  }
  function notice(text) { setMessages((items) => [...items, { id: crypto.randomUUID(), role: "assistant", text, sources: [] }]); }
  async function rebuild() {
    setIndexing(true); setMenu(false);
    try { const result = await request("/ingest", { method: "POST" }); setHealth({ state: "online", chunks: result.chunks }); notice(`Knowledge index ready: ${result.documents} documents, ${result.pages} pages, and ${result.chunks} searchable chunks.`); }
    catch (error) { notice(`I could not rebuild the index: ${error.message}`); checkHealth(); }
    finally { setIndexing(false); }
  }
  function selectSuggestion(value) { setQuestion(value); input.current?.focus(); }
  async function submit(event) {
    event.preventDefault(); const value = question.trim(); if (!value || asking) return;
    const pendingId = crypto.randomUUID();
    setMessages((items) => [...items, { id: crypto.randomUUID(), role: "user", text: value, sources: [] }, { id: pendingId, role: "assistant", pending: true, sources: [] }]);
    setQuestion(""); setAsking(true);
    try {
      const result = await request("/chat", { method: "POST", body: JSON.stringify({ question: value }) });
      setMessages((items) => items.map((item) => item.id === pendingId ? { ...item, pending: false, text: result.answer, sources: result.sources || [], trace: result.trace } : item));
    } catch (error) {
      setMessages((items) => items.map((item) => item.id === pendingId ? { ...item, pending: false, text: `I could not answer that question. ${error.message}`, sources: [] } : item));
    } finally { setAsking(false); requestAnimationFrame(() => input.current?.focus()); }
  }

  return <div className="app">
    <Sidebar health={health} indexing={indexing} onIndex={rebuild} open={menu} onClose={() => setMenu(false)}/>
    {menu && <button className="overlay" onClick={() => setMenu(false)} aria-label="Close menu"/>}
    <main className="main">
      <header className="topbar"><button className="icon-button menu" onClick={() => setMenu(true)}><Menu size={19}/></button><div className="top-title"><span>Customer support</span><strong>Ask the business documents</strong></div><Status health={health}/><div className="model"><Sparkles size={13}/>Gemini 3.5 Flash-Lite</div></header>
      <div className="workspace"><section className="chat"><div className="conversation">{messages.length === 1 && <Welcome onSelect={selectSuggestion}/>}<div className="message-list">{messages.map((message) => <Message message={message} key={message.id}/>)}<div ref={end}/></div></div>
        <footer><form onSubmit={submit}><input ref={input} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about returns, delivery, warranty, or instructions…" disabled={asking} maxLength={1000}/><button disabled={asking || question.trim().length < 2}>{asking ? <LoaderCircle className="spin"/> : <ArrowUp/>}</button></form><p><ShieldCheck size={12}/>Grounded in approved documents · Verify important decisions</p></footer>
      </section><Evidence sources={latestSources} trace={latestTrace}/></div>
    </main>
  </div>;
}
