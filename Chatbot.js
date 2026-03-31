import { useState, useRef, useEffect } from "react";

export default function Chatbot() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = () => {
    if (!input.trim()) return;

    const userText = input.toLowerCase();

    const userMsg = { type: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    setTyping(true);

    setTimeout(() => {
      let reply = "I'm here to help you with government schemes.";

      // 🔥 FAKE AI LOGIC
      if (userText.includes("housing") || userText.includes("home")) {
        reply = "You can check PM Awas Yojana for affordable housing support.";
      } 
      else if (
        userText.includes("education") ||
        userText.includes("student") ||
        userText.includes("scholarship")
      ) {
        reply = "There are multiple scholarship and skill development schemes available.";
      } 
      else if (userText.includes("income") || userText.includes("low income")) {
        reply = "Low income individuals can benefit from subsidy and welfare schemes.";
      } 
      else if (userText.includes("job") || userText.includes("employment")) {
        reply = "You can explore skill development and employment schemes provided by the government.";
      }
      else if (userText.includes("hello") || userText.includes("hi")) {
        reply = "Hello 👾! Ask me about schemes, eligibility, or benefits.";
      }

      const botMsg = {
        type: "bot",
        text: reply
      };

      setMessages((prev) => [...prev, botMsg]);
      setTyping(false);
    }, 800);
  };

  return (
    <>
      {/* Floating Button */}
      <div className="chatbot-btn" onClick={() => setOpen(!open)}>
        💬
      </div>

      {/* Chatbox */}
      {open && (
        <div className="chatbox">
          {/* Header */}
          <div className="chat-header">
            AI Assistant 👾
            <span className="close-btn" onClick={() => setOpen(false)}>
              ✖
            </span>
          </div>

          {/* Messages */}
          <div className="chat-body">
            {messages.length === 0 && (
              <p className="welcome">
                Hi! Ask me anything about government schemes 👾
              </p>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`msg ${msg.type}`}>
                {msg.text}
              </div>
            ))}

            {/* Typing Animation */}
            {typing && (
              <div className="msg bot typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}

            <div ref={chatEndRef}></div>
          </div>

          {/* Input */}
          <div className="chat-input">
            <input
              value={input}
              placeholder="Ask something..."
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage} disabled={typing}>
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}