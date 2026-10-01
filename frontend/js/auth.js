document.addEventListener('DOMContentLoaded', () => {
  if (api.getToken()) {
    window.location.href = '/';
  }

  const loginTab = document.getElementById('login-tab');
  const registerTab = document.getElementById('register-tab');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const errorDiv = document.getElementById('error-msg');

  function switchTab(tab) {
    errorDiv.textContent = '';
    if (tab === 'login') {
      loginTab.classList.add('active');
      registerTab.classList.remove('active');
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
    } else {
      registerTab.classList.add('active');
      loginTab.classList.remove('active');
      registerForm.style.display = 'block';
      loginForm.style.display = 'none';
    }
  }

  loginTab.addEventListener('click', () => switchTab('login'));
  registerTab.addEventListener('click', () => switchTab('register'));

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-pass').value;

    try {
      const res = await api.login(email, pass);
      api.setToken(res.access_token);
      window.location.href = '/';
    } catch (err) {
      errorDiv.textContent = err.message;
    }
  });

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-user').value;
    const email = document.getElementById('reg-email').value;
    const pass = document.getElementById('reg-pass').value;
    const confirm = document.getElementById('reg-confirm').value;

    if (!email.endsWith('@abes.ac.in')) {
      errorDiv.textContent = 'Email must end with @abes.ac.in';
      return;
    }
    if (pass !== confirm) {
      errorDiv.textContent = 'Passwords do not match';
      return;
    }

    try {
      const res = await api.register(username, email, pass);
      api.setToken(res.access_token);
      window.location.href = '/';
    } catch (err) {
      errorDiv.textContent = err.message;
    }
  });
});
