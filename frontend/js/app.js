let currentUser = null;
let currentConversationId = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!api.getToken()) {
    window.location.href = '/login.html';
    return;
  }

  try {
    currentUser = await api.getMe();
    document.getElementById('user-name').textContent = currentUser.username;
    if (currentUser.role === 'admin') {
      document.getElementById('admin-link').style.display = 'inline';
    }
    loadConversations();
  } catch (err) {
    console.error('Failed to load user', err);
  }

  document.getElementById('logout-btn').addEventListener('click', () => {
    api.clearToken();
    window.location.href = '/login.html';
  });

  document.getElementById('new-chat-btn').addEventListener('click', () => {
    currentConversationId = null;
    document.getElementById('messages-container').innerHTML = '<div class="message bot">Welcome! How can I help you today?</div>';
    document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('active'));
  });

  document.getElementById('send-btn').addEventListener('click', sendMessage);
  document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});

async function loadConversations() {
  const list = document.getElementById('conv-list');
  try {
    const convs = await api.getConversations();
    list.innerHTML = '';
    convs.forEach(c => {
      const li = document.createElement('li');
      li.className = 'conversation-item';
      if (c.id === currentConversationId) li.classList.add('active');
      const title = (c.title || 'New Conversation').substring(0, 30);
      li.innerHTML = `<span title="${c.title || ''}">${title}<br><small>${new Date(c.created_at).toLocaleDateString()}</small></span> <button class="delete-conv" data-id="${c.id}">✕</button>`;
      li.onclick = (e) => {
        if(e.target.classList.contains('delete-conv')) return;
        selectConversation(c.id);
      };
      const delBtn = li.querySelector('.delete-conv');
      delBtn.onclick = async () => {
        await api.deleteConversation(c.id);
        if(currentConversationId === c.id) document.getElementById('new-chat-btn').click();
        loadConversations();
      };
      list.appendChild(li);
    });
  } catch(e) { console.error(e); }
}

async function selectConversation(id) {
  currentConversationId = id;
  const container = document.getElementById('messages-container');
  container.innerHTML = '<div class="message bot">Loading...</div>';
  document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('active'));
  try {
    const msgs = await api.getMessages(id);
    container.innerHTML = '';
    msgs.forEach(m => {
      if (m.role === 'user') {
        appendMessage(m.content, 'user');
      } else if (m.role === 'assistant') {
        let sources = [];
        try { if (m.sources_json) sources = JSON.parse(m.sources_json); } catch(e) {}
        appendMessage(m.content, 'bot', sources, m.id);
      }
    });
    scrollToBottom();
  } catch(e) { console.error(e); }
}

async function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  input.disabled = true;
  document.getElementById('send-btn').disabled = true;

  appendMessage(text, 'user');
  
  const typing = document.createElement('div');
  typing.className = 'typing';
  typing.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  document.getElementById('messages-container').appendChild(typing);
  scrollToBottom();

  try {
    const res = await api.sendMessage(text, currentConversationId);
    typing.remove();
    if (!currentConversationId) {
      currentConversationId = res.conversation_id;
      loadConversations();
    }
    appendMessage(res.response, 'bot', res.sources, res.message_id);
  } catch (err) {
    typing.remove();
    appendMessage('Error processing request.', 'bot');
  }

  input.disabled = false;
  document.getElementById('send-btn').disabled = false;
  input.focus();
}

function appendMessage(text, sender, sources = [], messageId = null) {
  const container = document.getElementById('messages-container');
  const div = document.createElement('div');
  div.className = `message ${sender}`;
  div.textContent = text; // basic text handling for simplicity

  if (sender === 'bot' && sources && sources.length > 0) {
    const srcDiv = document.createElement('div');
    srcDiv.className = 'sources';
    srcDiv.innerHTML = '<strong>Sources:</strong>';
    sources.forEach(s => {
      srcDiv.innerHTML += `<div class="source-item">${s.source} (Page ${s.page}) - Relevance: ${s.relevance_score.toFixed(2)}</div>`;
    });
    div.appendChild(srcDiv);
  }

  if (sender === 'bot' && messageId) {
    const fbDiv = document.createElement('div');
    fbDiv.className = 'feedback-btns';
    fbDiv.innerHTML = `
      <button class="feedback-btn" onclick="submitFeedback('${messageId}', 5)">👍</button>
      <button class="feedback-btn" onclick="submitFeedback('${messageId}', 1)">👎</button>
    `;
    div.appendChild(fbDiv);
  }

  container.appendChild(div);
  scrollToBottom();
}

function scrollToBottom() {
  const container = document.getElementById('messages-container');
  container.scrollTop = container.scrollHeight;
}

window.submitFeedback = async function(msgId, rating) {
  try {
    await api.submitFeedback(msgId, rating, '');
    alert('Feedback submitted!');
  } catch (err) {
    console.error(err);
  }
}
