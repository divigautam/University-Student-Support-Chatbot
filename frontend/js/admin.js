document.addEventListener('DOMContentLoaded', async () => {
  if (!api.getToken()) {
    window.location.href = '/login.html';
    return;
  }

  try {
    const user = await api.getMe();
    if (user.role !== 'admin') {
      window.location.href = '/';
      return;
    }
    document.getElementById('user-name').textContent = user.username;
    
    loadDashboard();
    loadDocuments();
  } catch (err) {
    window.location.href = '/login.html';
  }

  document.getElementById('logout-btn').addEventListener('click', () => {
    api.clearToken();
    window.location.href = '/login.html';
  });

  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-upload');

  uploadZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', handleUpload);
});

async function loadDashboard() {
  try {
    const data = await api.getDashboard();
    document.getElementById('total-convs').textContent = data.total_conversations || 0;
    document.getElementById('total-msgs').textContent = data.total_messages || 0;
    document.getElementById('total-users').textContent = data.total_users || 0;
    document.getElementById('total-docs').textContent = data.total_documents || 0;
  } catch(e) { console.error(e); }
}

async function loadDocuments() {
  try {
    const docs = await api.getDocuments();
    const tbody = document.querySelector('#docs-table tbody');
    tbody.innerHTML = '';
    docs.forEach(d => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${d.filename}</td>
        <td><span class="badge ${d.status}">${d.status}</span></td>
        <td>${new Date(d.upload_time).toLocaleDateString()}</td>
        <td>
          <button onclick="reindexDoc('${d.id}')">Reindex</button>
          <button onclick="deleteDoc('${d.id}')" style="color:red;">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch(e) { console.error(e); }
}

async function handleUpload(e) {
  const file = e.target.files[0];
  if (!file || !file.name.endsWith('.pdf')) {
    alert('Only PDFs are allowed');
    return;
  }
  
  try {
    await api.uploadDocument(file);
    alert('Upload successful');
    loadDocuments();
    loadDashboard();
  } catch (err) {
    alert('Upload failed: ' + err.message);
  }
}

window.deleteDoc = async function(id) {
  if(!confirm('Are you sure?')) return;
  try {
    await api.deleteDocument(id);
    loadDocuments();
  } catch(e) { console.error(e); }
};

window.reindexDoc = async function(id) {
  try {
    await api.reindexDocument(id);
    alert('Reindexing started');
    loadDocuments();
  } catch(e) { console.error(e); }
};
