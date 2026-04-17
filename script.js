const chatBox = document.getElementById("chat-box");

let chats = {};
let currentChat = "chat1";
let chatTitles = {};

// ================== STORAGE ==================
function saveToLocal() {
    localStorage.setItem("chats", JSON.stringify(chats));
    localStorage.setItem("titles", JSON.stringify(chatTitles));
}

function loadFromLocal() {
    const savedChats = localStorage.getItem("chats");
    const savedTitles = localStorage.getItem("titles");

    if (savedChats) chats = JSON.parse(savedChats);
    if (savedTitles) chatTitles = JSON.parse(savedTitles);
}

// ================== MESSAGE ==================
function addMessage(text, className) {
    const div = document.createElement("div");
    div.className = "message " + className;

    // typing effect
    let i = 0;
    function type() {
        if (i < text.length) {
            div.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, 10);
        }
    }
    type();

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;

    // save memory
    chats[currentChat].push({ text, className });
    saveToLocal();

    // auto title
    if (!chatTitles[currentChat]) {
        let lower = text.toLowerCase();

        if (lower.includes("science")) {
            chatTitles[currentChat] = "🌱 Science Projects";
        } else if (lower.includes("arduino")) {
            chatTitles[currentChat] = "🔧 Arduino Ideas";
        } else if (lower.includes("ai")) {
            chatTitles[currentChat] = "🤖 AI Projects";
        } else {
            chatTitles[currentChat] = "💬 General Chat";
        }
    }

    renderHistory();
}

// ================== SEND ==================
function sendMessage() {
    const input = document.getElementById("input");
    const message = input.value.trim();

    if (!message) return;

    addMessage(message, "user");

    // 🤖 thinking
    const thinkingDiv = document.createElement("div");
    thinkingDiv.className = "message bot";
    thinkingDiv.innerHTML = "🤖 Soch raha hu...";
    chatBox.appendChild(thinkingDiv);

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.text())
    .then(data => {
        thinkingDiv.remove();
        addMessage(data, "bot");
    });

    input.value = "";
}

// ================== HISTORY ==================
function renderHistory() {
    const historyDiv = document.getElementById("history");
    historyDiv.innerHTML = "";

    Object.keys(chats).forEach(chatId => {
        const div = document.createElement("div");
        div.className = "history-item";
        div.innerText = chatTitles[chatId] || "💬 New Chat";

        div.onclick = () => loadChat(chatId);
        historyDiv.appendChild(div);
    });
}

function loadChat(chatId) {
    currentChat = chatId;
    chatBox.innerHTML = "";

    chats[chatId].forEach(msg => {
        const div = document.createElement("div");
        div.className = "message " + msg.className;
        div.innerHTML = msg.text;
        chatBox.appendChild(div);
    });
}

// ================== CHAT CONTROL ==================
function newChat() {
    currentChat = "chat" + Date.now();
    chats[currentChat] = [];
    chatBox.innerHTML = "";
    renderHistory();
}

function clearChat() {
    chatBox.innerHTML = "";
}

function saveChat() {
    const text = chatBox.innerText;
    const blob = new Blob([text], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "chat.txt";
    a.click();
}

// ================== VOICE ==================
function startMic() {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = "en-IN";

    recognition.onresult = function(event) {
        document.getElementById("input").value =
            event.results[0][0].transcript;
    };

    recognition.start();
}

// ================== ENTER KEY ==================
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("input");

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
});

// ================== INIT ==================
loadFromLocal();
newChat();
renderHistory();