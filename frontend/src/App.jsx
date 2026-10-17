
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/agent";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(event) {
    event.preventDefault();

    const message = question.trim();
    if (!message || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: message },
    ]);
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer || "No answer was returned.",
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      setError(
        `${err.message}. Check that the backend is running and CORS is configured.`
      );
    } finally {
      setLoading(false);
    }
  }

  function newConversation() {
    setMessages([]);
    setConversationId(null);
    setError("");
    setQuestion("");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">G</div>
          <div>
            <h2>GeoPulse <span>AI</span></h2>
            <p>GEOPOLITICAL INTELLIGENCE</p>
          </div>
        </div>

        <button className="new-chat" onClick={newConversation}>
          <span>＋</span> New conversation
        </button>

        <div className="side-label">RESEARCH TOOLS</div>
        <div className="side-item">◈ &nbsp; Geopolitical analysis</div>
        <div className="side-item">◎ &nbsp; Country research</div>
        <div className="side-item">◷ &nbsp; Conflict timelines</div>
        <div className="side-item">⇄ &nbsp; Country comparison</div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <span>Local research backend</span>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <span className="eyebrow">INTELLIGENCE WORKSPACE</span>
            <h1>Research Assistant</h1>
          </div>
          <div className="connection">
            <span className="status-dot" />
            API workspace
          </div>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">✳</div>
              <p className="eyebrow">WELCOME TO GEOPULSE AI</p>
              <h2>Understand the world<br />with better context.</h2>
              <p className="welcome-description">
                Ask geopolitical questions and explore answers grounded
                in your research documents.
              </p>

              <div className="suggestions">
                <button onClick={() => setQuestion("What is NATO?")}>
                  <strong>What is NATO?</strong>
                  <span>Explore the alliance and its purpose</span>
                </button>
                <button
                  onClick={() =>
                    setQuestion("What is the role of the UN Security Council?")
                  }
                >
                  <strong>UN Security Council</strong>
                  <span>Explore its role and responsibilities</span>
                </button>
                <button
                  onClick={() =>
                    setQuestion("What is the purpose of the United Nations?")
                  }
                >
                  <strong>United Nations</strong>
                  <span>Research its purpose and mission</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((item, index) => (
                <article
                  className={`message ${item.role}`}
                  key={`${index}-${item.role}`}
                >
                  <div className="avatar">
                    {item.role === "user" ? "Y" : "G"}
                  </div>
                  <div className="message-body">
                    <div className="message-author">
                      {item.role === "user" ? "You" : "GeoPulse AI"}
                    </div>
                    <div className="message-text">{item.content}</div>

                    {item.sources?.length > 0 && (
                      <div className="sources">
                        <strong>Sources used</strong>
                        <div className="source-list">
                          {item.sources.map((source) => (
                            <span className="source-tag" key={source}>
                              ▤ {source}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </article>
              ))}

              {loading && (
                <div className="loading">
                  <span className="status-dot" />
                  GeoPulse AI is researching...
                </div>
              )}
            </div>
          )}

          {error && <div className="error-message">{error}</div>}
        </section>

        <footer className="composer-area">
          <form className="composer" onSubmit={sendMessage}>
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a geopolitical research question..."
              disabled={loading}
              aria-label="Research question"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              aria-label="Send message"
            >
              {loading ? "…" : "↑"}
            </button>
          </form>
          <p className="disclaimer">
            Answers depend on available documents. Verify important claims
            against the original sources.
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;

  