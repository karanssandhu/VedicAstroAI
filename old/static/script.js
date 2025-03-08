function sendQuestion() {
  const question = document.getElementById('question').value.trim();
  if (!question) return;

  const messages = document.getElementById('messages');
  messages.innerHTML += `<div class="message"><strong>You:</strong> ${question}</div>`;
  document.getElementById('question').value = '';
  messages.scrollTop = messages.scrollHeight;

  $.ajax({
      type: 'POST',
      url: '/query',
      contentType: 'application/json',
      data: JSON.stringify({ chart: chart, question: question }),
      success: function(data) {
          typeResponse(data.response, data.reasoning);
      },
      error: function() {
          messages.innerHTML += `<div class="message"><strong>AI:</strong> The cosmos are silent... try again.</div>`;
      }
  });
}

function typeResponse(text, reasoning) {
  const messages = document.getElementById('messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message';
  messages.appendChild(messageDiv);

  let i = 0;
  const fullText = `<strong>AI:</strong> ${text}<br><span class="reasoning">${reasoning}</span>`;
  function type() {
      if (i < fullText.length) {
          messageDiv.innerHTML = fullText.substring(0, i + 1);
          i++;
          setTimeout(type, 20); // Typing speed
      }
  }
  type();
  messages.scrollTop = messages.scrollHeight;
}

document.getElementById('question').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') sendQuestion();
});