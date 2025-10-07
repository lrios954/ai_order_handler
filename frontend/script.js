const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  const container = document.getElementById("order");
  container.innerHTML = "";

  data.items.forEach(item => {
    const div = document.createElement("div");
    div.innerHTML = `
      <img src="${item.image}" width="200" style="vertical-align: middle" />
      <strong>${item.name}</strong> x ${item.quantity} - 
      $${item.subtotal.toFixed(2)}
    `;
    container.appendChild(div);
  });

  document.getElementById("total").textContent = data.total.toFixed(2);
};

// 🎤 Voice recognition setup
let recognition;
if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US"; // or "es-ES" if you want Spanish

  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    console.log("User said:", transcript);
    ws.send(transcript);
  };

  recognition.onerror = function(event) {
    console.error("Speech recognition error:", event.error);
  };
}

function startListening() {
  if (recognition) {
    recognition.start();
  } else {
    alert("Speech Recognition not supported in this browser");
  }
}
