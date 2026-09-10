/* ============================================================
   SIGNLANG – script.js
   Handles: Auth, Login/Signup toggle, Language Info panels,
   Dark Mode, Settings, Navigation utilities
   ============================================================ */

let isLogin = true;

// =========================================================
// AUTH: Toggle between Login and Signup forms
// =========================================================
function toggleForm() {
    isLogin = !isLogin;

    const formTitle    = document.getElementById('form-title');
    const formSubtitle = document.getElementById('form-subtitle');
    const nameGroup    = document.getElementById('name-group');
    const confirmGroup = document.getElementById('confirm-group');
    const btnLabel     = document.getElementById('btn-label');
    const toggleText   = document.getElementById('toggleText');
    const badge        = document.getElementById('form-mode-badge');
    const error        = document.getElementById('error');

    error.textContent = '';

    if (isLogin) {
        formTitle.textContent    = 'Login';
        formSubtitle.textContent = 'Sign in to access your Sign Language dashboard.';
        badge.textContent        = 'Welcome Back 👋';
        btnLabel.textContent     = 'Sign In';
        nameGroup.style.display    = 'none';
        confirmGroup.style.display = 'none';
        toggleText.innerHTML = 'Don\'t have an account? <span onclick="toggleForm()">Sign Up</span>';
    } else {
        formTitle.textContent    = 'Create Account';
        formSubtitle.textContent = 'Join SignLang and start breaking communication barriers.';
        badge.textContent        = 'New Here? 🙌';
        btnLabel.textContent     = 'Create Account';
        nameGroup.style.display    = 'block';
        confirmGroup.style.display = 'block';
        toggleText.innerHTML = 'Already have an account? <span onclick="toggleForm()">Login</span>';
    }
}

// =========================================================
// AUTH: Handle Login & Signup submission
// =========================================================
function handleAuth() {
    const user       = document.getElementById('username').value.trim();
    const pass       = document.getElementById('password').value;
    const confirmPwd = document.getElementById('confirmPassword')
                         ? document.getElementById('confirmPassword').value
                         : '';
    const error      = document.getElementById('error');
    const submitBtn  = document.getElementById('submit-btn');

    error.textContent = '';

    // Basic validation
    if (!user || !pass) {
        error.textContent = '⚠ Please fill in all required fields.';
        return;
    }

    if (isLogin) {
        // LOGIN FLOW
        const savedUser = localStorage.getItem('sl_user');
        const savedPass = localStorage.getItem('sl_pass');

        if (user === savedUser && pass === savedPass) {
            submitBtn.innerHTML = '<span>Signing in…</span> <i class="fa-solid fa-circle-notch fa-spin"></i>';
            submitBtn.disabled  = true;

            setTimeout(() => {
                localStorage.setItem('sl_login', 'true');
                window.location.href = '/home';
            }, 1000);
        } else {
            error.textContent = '✖ Invalid username or password.';
        }

    } else {
        // SIGNUP FLOW
        if (pass !== confirmPwd) {
            error.textContent = '✖ Passwords do not match.';
            return;
        }
        if (pass.length < 6) {
            error.textContent = '✖ Password must be at least 6 characters.';
            return;
        }

        localStorage.setItem('sl_user', user);
        localStorage.setItem('sl_pass', pass);

        submitBtn.innerHTML = '<span>Creating account…</span> <i class="fa-solid fa-circle-notch fa-spin"></i>';
        submitBtn.disabled  = true;

        setTimeout(() => {
            alert('✅ Account created! Please log in.');
            submitBtn.innerHTML  = '<span id="btn-label">Sign In</span> <i class="fa-solid fa-arrow-right"></i>';
            submitBtn.disabled   = false;
            isLogin = true; // Force reset so toggleForm goes to login state
            isLogin = false;
            toggleForm();   // Call toggle (from false → true = login)
        }, 900);
    }
}

// Allow submitting form on Enter key press
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const btn = document.getElementById('submit-btn');
        if (btn) btn.click();
    }
});

// =========================================================
// PASSWORD VISIBILITY TOGGLE
// =========================================================
function togglePassword(inputId, eyeId) {
    const input = document.getElementById(inputId);
    const eye   = document.getElementById(eyeId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (eye) eye.className = 'fa-regular fa-eye-slash';
    } else {
        input.type = 'password';
        if (eye) eye.className = 'fa-regular fa-eye';
    }
}

// =========================================================
// LOGOUT
// =========================================================
function logout() {
    localStorage.removeItem('sl_login');
    window.location.href = '/login.html';
}

// =========================================================
// PROTECT HOME PAGE (runs on home.html only)
// =========================================================
if (window.location.pathname.includes('home.html')) {
    if (localStorage.getItem('sl_login') !== 'true') {
        window.location.href = 'login.html';
    } else {
        // Show the saved username in the navbar
        const savedUser = localStorage.getItem('sl_user') || 'User';
        const navUser   = document.getElementById('nav-username');
        if (navUser) navUser.textContent = savedUser;
    }
}

// =========================================================
// SMOOTH SCROLL TO SECTION
// =========================================================
function scrollToSection(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

// =========================================================
// SIGN LANGUAGE INFO PANEL
// Full detailed content for ASL and ISL
// =========================================================
const langData = {
    asl: {
        flag: '🇺🇸',
        name: 'American Sign Language (ASL)',
        short: 'ASL',
        badge: 'Supported in SignLang',
        overview: 'American Sign Language (ASL) is a complete, natural language that serves as the predominant sign language of deaf communities in the United States and most of anglophone Canada. It is a rich visual-gestural language with its own grammar, syntax, and vocabulary — entirely independent of English.',
        facts: [
            'Used by approximately 500,000 – 2 million people in the USA',
            'ASL is derived from Old French Sign Language (LSF)',
            'It has its own complex grammar, distinct from English',
            'Recognized as an official language in the US for education',
            'Handshape, movement, location, and facial expression are key parameters'
        ],
        grammar: 'ASL uses a Topic-Comment structure rather than Subject-Verb-Object. Facial expressions carry grammatical meaning (e.g., raised eyebrows for yes/no questions). Spatial grammar is used to indicate relationships between entities.',
        gestures: ['Handshape', 'Palm Orientation', 'Location', 'Movement', 'Non-Manual Signals'],
        coverage: [
            { label: 'Alphabets (A–Z)', pct: 100 },
            { label: 'Numbers (0–9)', pct: 100 },
            { label: 'Common Words', pct: 78 },
            { label: 'Phrases', pct: 55 }
        ],
        system: 'Our system is trained on an ASL dataset covering all 26 letters of the alphabet and 52 common words including greetings, emotions, actions, and daily vocabulary. We use MediaPipe Hands for 21-point landmark extraction and an LSTM classifier for gesture recognition.'
    },
    isl: {
        flag: '🇮🇳',
        name: 'Indian Sign Language (ISL)',
        short: 'ISL',
        badge: 'Supported in SignLang',
        overview: 'Indian Sign Language (ISL) is the sign language used by the deaf community in India. It is a complete natural language with its own grammar and structure, quite different from spoken Indian languages. ISL is used across India and has rich regional variations reflecting India\'s linguistic diversity.',
        facts: [
            'Used by an estimated 18+ million deaf people across India',
            'ISL has dialects that vary across regions (North, South, East, West)',
            'Officially recognized by the Indian government in recent years',
            'ISL is distinct from BSL and ASL despite some visual similarities',
            'Two-handed manual alphabet is a key feature of ISL'
        ],
        grammar: 'ISL typically follows a Subject-Object-Verb (SOV) word order, similar to spoken Hindi. Spatial grammar and classifiers are used extensively. Mouth movements and facial expressions play important roles in conveying meaning and sentence types.',
        gestures: ['Two-Hand Shapes', 'Spatial Signing', 'Mouth Patterns', 'Eye Gaze', 'Body Posture'],
        coverage: [
            { label: 'ISL Alphabets', pct: 100 },
            { label: 'Numbers (0–9)', pct: 100 },
            { label: 'Common Words', pct: 65 },
            { label: 'Phrases', pct: 42 }
        ],
        system: 'Our ISL module is trained on an ISL-specific gesture dataset using a two-handed landmark tracking pipeline. It covers the full ISL alphabet, basic numerals, and a vocabulary of 40+ common words. The model uses a CNN+LSTM architecture for frame sequence classification.'
    }
};

function showInfo(type) {
    const panel = document.getElementById('languageInfo');
    const data  = langData[type];
    if (!panel || !data) return;

    // Highlight active button
    document.querySelectorAll('.lang-select-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById('btn-' + type);
    if (activeBtn) activeBtn.classList.add('active');

    // Build coverage bars HTML
    const barsHTML = data.coverage.map(item => `
        <div class="system-coverage-bar">
            <span class="bar-label">${item.label}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width: ${item.pct}%"></div>
            </div>
            <span class="bar-pct">${item.pct}%</span>
        </div>
    `).join('');

    // Build gesture chips HTML
    const chipsHTML = data.gestures.map(g => `<span class="gesture-chip">${g}</span>`).join('');

    // Build facts list HTML
    const factsHTML = data.facts.map(f => `<li>${f}</li>`).join('');

    // Inject full HTML
    panel.innerHTML = `
        <div class="info-header">
            <span class="info-flag">${data.flag}</span>
            <div class="info-header-text">
                <div class="info-badge">${data.badge}</div>
                <h3>${data.name}</h3>
                <p>${data.overview}</p>
            </div>
        </div>

        <div class="info-section-grid">
            <div class="info-block">
                <h4><i class="fa-solid fa-circle-info"></i> Key Facts</h4>
                <ul>${factsHTML}</ul>
            </div>

            <div class="info-block">
                <h4><i class="fa-solid fa-code-branch"></i> Grammar Structure</h4>
                <p>${data.grammar}</p>
            </div>
        </div>

        <div class="info-section-grid">
            <div class="info-block">
                <h4><i class="fa-solid fa-hand"></i> Core Sign Parameters</h4>
                <div class="info-gestures-row">${chipsHTML}</div>
            </div>

            <div class="info-block">
                <h4><i class="fa-solid fa-chart-bar"></i> System Coverage</h4>
                ${barsHTML}
            </div>
        </div>

        <div class="info-full-width">
            <h4><i class="fa-solid fa-robot"></i> How Our System Handles ${data.short}</h4>
            <p>${data.system}</p>
        </div>
    `;

    // Animate in
    panel.classList.remove('visible');
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            panel.classList.add('visible');
        });
    });
}

// =========================================================
// SETTINGS MODAL (Dark Mode)
// =========================================================
function openSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) modal.classList.add('open');
    // Reflect current dark mode state on toggle
    const isDark   = document.body.classList.contains('dark-mode');
    const toggle   = document.getElementById('dark-toggle');
    if (toggle) {
        toggle.classList.toggle('on', isDark);
    }
}

function closeSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) modal.classList.remove('open');
}

function toggleDarkMode() {
    const toggle = document.getElementById('dark-toggle');
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    if (toggle) toggle.classList.toggle('on', isDark);
    localStorage.setItem('sl_theme', isDark ? 'dark' : 'light');
}

// Apply saved theme on load
(function applySavedTheme() {
    if (localStorage.getItem('sl_theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }
})();

// Close settings modal when clicking outside the box
document.addEventListener('click', function(e) {
    const modal = document.getElementById('settings-modal');
    const box   = document.querySelector('.settings-box');
    if (modal && modal.classList.contains('open') && !box.contains(e.target)) {
        const sliders = document.querySelector('[onclick="openSettings()"]');
        if (sliders && !sliders.contains(e.target)) {
            closeSettings();
        }
    }
});

// =========================================================
// CAMERA (kept for backend team integration)
// =========================================================
function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            const vid = document.getElementById('video');
            if (vid) vid.srcObject = stream;
        })
        .catch(() => {
            alert('Camera access denied! Please allow camera permissions.');
        });
}