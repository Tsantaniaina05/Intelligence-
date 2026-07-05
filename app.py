import os
import sqlite3
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
DB_FILE = "database.db"

# ==========================================
# INITIALISATION DE LA BASE DE DONNÉES (SQLite)
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    # Création du compte Admin par défaut si inexistant
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # Admin est approuvé par défaut (1)
        cursor.execute("INSERT INTO users (username, password, name, is_approved) VALUES ('admin', 'admin123', 'Tsanta Creator', 1)")
    conn.commit()
    conn.close()

init_db()

# ==========================================
# INTERFACE HTML PREMIUM V4 (WITH AUTH & ADMIN)
# ==========================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lou Tsanta — Système Sécurisé</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background-color: #080a0f; color: #f1f5f9; display: flex; justify-content: center; height: 100vh; height: 100dvh; overflow: hidden; }
        
        .chat-container { 
            width: 100%; max-width: 850px; display: flex; flex-direction: column; height: 100vh; height: 100dvh; 
            background: #0f111a; position: relative; border-left: 1px solid rgba(255, 46, 99, 0.08); border-right: 1px solid rgba(255, 46, 99, 0.08);
        }

        /* PANNEAUX D'AUTH / DESIGN FORMULAIRES */
        .auth-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(8, 10, 15, 0.98);
            backdrop-filter: blur(20px); z-index: 100; display: flex; justify-content: center; align-items: center; padding: 20px;
        }
        .auth-box {
            background: #161925; border: 1px solid rgba(255, 46, 99, 0.25); box-shadow: 0 0 30px rgba(255, 46, 99, 0.15);
            padding: 30px; border-radius: 24px; width: 100%; max-width: 400px; text-align: center;
        }
        .auth-box h2 { font-size: 1.4rem; color: #ffffff; margin-bottom: 8px; text-shadow: 0 0 10px rgba(255, 46, 99, 0.3); }
        .auth-box p { font-size: 0.85rem; color: #9ca3af; margin-bottom: 20px; }
        .input-group { background: #080a0f; border: 1px solid rgba(255, 46, 99, 0.15); border-radius: 14px; padding: 4px 12px; display: flex; align-items: center; margin-bottom: 12px; }
        .input-group:focus-within { border-color: #ff2e63; box-shadow: 0 0 8px rgba(255, 46, 99, 0.2); }
        .input-group input { flex: 1; background: transparent; border: none; color: white; outline: none; padding: 10px 0; font-size: 0.95rem; }
        
        .auth-btn { background: linear-gradient(135deg, #ff2e63 0%, #b80d57 100%); color: white; border: none; padding: 12px; border-radius: 14px; cursor: pointer; font-weight: 600; width: 100%; margin-top: 8px; box-shadow: 0 4px 12px rgba(255, 46, 99, 0.3); transition: all 0.2s; }
        .auth-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(255, 46, 99, 0.4); }
        .switch-link { color: #ff2e63; font-size: 0.82rem; cursor: pointer; display: inline-block; margin-top: 14px; text-decoration: underline; }

        /* HEADER */
        .header { padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; background: rgba(15, 17, 26, 0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255, 46, 99, 0.15); z-index: 10; min-height: 75px; }
        .header-main { display: flex; align-items: center; gap: 10px; }
        .header h1 { font-size: 1.25rem; color: #ffffff; font-weight: 700; text-shadow: 0 0 10px rgba(255, 46, 99, 0.3); }
        .status-dot { width: 8px; height: 8px; background-color: #ff2e63; border-radius: 50%; box-shadow: 0 0 10px #ff2e63; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
        .header .author { font-size: 0.72rem; color: #9ca3af; margin-top: 3px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; opacity: 0.7; }
        .header-actions { display: flex; gap: 8px; }
        .nav-btn { background: rgba(255, 46, 99, 0.06); border: 1px solid rgba(255, 46, 99, 0.2); color: #ff2e63; padding: 8px 12px; border-radius: 14px; cursor: pointer; font-size: 0.78rem; font-weight: 600; transition: all 0.2s; }
        .nav-btn:hover { background: #ff2e63; color: white; }

        /* ZONE MESSAGES */
        .chat-box { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; background: linear-gradient(180deg, #0f111a 0%, #090a0f 100%); }
        .msg { max-width: 85%; padding: 14px 18px; border-radius: 18px; line-height: 1.6; font-size: 0.96rem; word-wrap: break-word; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); }
        .user { background: linear-gradient(135deg, #ff2e63 0%, #b80d57 100%); color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; white-space: pre-wrap; }
        .bot { background: #161925; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid rgba(255, 46, 99, 0.1); }
        
        /* CODES DANS CHAT */
        .bot pre { background: #080a0f !important; border-left: 3px solid #ff2e63 !important; border: 1px solid rgba(255, 46, 99, 0.15); padding: 14px !important; margin: 14px 0 !important; overflow-x: auto !important; border-radius: 8px !important; }
        .bot code { font-family: monospace !important; color: #f1f5f9 !important; font-size: 0.88rem !important; }
        .bot p code { background: #080a0f !important; color: #ff2e63 !important; padding: 2px 6px !important; border-radius: 4px !important; }
        
        .msg-actions { display: flex; justify-content: flex-end; margin-top: 8px; }
        .copy-btn { background: rgba(255, 46, 99, 0.05); border: 1px solid rgba(255, 46, 99, 0.2); color: #ff2e63; padding: 4px 10px; font-size: 0.72rem; cursor: pointer; border-radius: 6px; }
        .copy-btn:hover { background: #ff2e63; color: white; }

        /* LOADER */
        .loading-msg { display: none; align-self: flex-start; background: #161925; padding: 14px 18px; border-radius: 18px; border: 1px solid rgba(255, 46, 99, 0.15); color: #9ca3af; align-items: center; gap: 12px; }
        .spinner { width: 16px; height: 16px; border: 2px solid rgba(255, 46, 99, 0.1); border-top-color: #ff2e63; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ZONE D'ENTRÉE */
        .input-container { padding: 18px 24px 28px 24px; background: #0f111a; border-top: 1px solid rgba(255, 46, 99, 0.15); }
        .input-wrapper { display: flex; align-items: center; background: #161925; border: 1px solid rgba(255, 46, 99, 0.15); border-radius: 28px; padding: 6px 8px 6px 18px; }
        .input-wrapper:focus-within { border-color: #ff2e63; background: #1d2133; }
        input[type="text"] { flex: 1; background: transparent; border: none; color: #ffffff; font-size: 0.98rem; outline: none; padding: 10px 0; }
        .send-btn { background: #ff2e63; color: white; border: none; width: 38px; height: 38px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; padding-bottom: 2px; box-shadow: 0 0 10px rgba(255, 46, 99, 0.3); }

        /* PANNEAU ADMIN */
        .admin-panel { padding: 20px; overflow-y: auto; flex: 1; display: none; background: #090a0f; }
        .admin-panel h2 { margin-bottom: 20px; color: #fff; font-size: 1.3rem; border-bottom: 1px solid rgba(255,46,99,0.2); padding-bottom: 10px; }
        .user-row { background: #161925; padding: 14px 20px; border-radius: 14px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
        .user-info { display: flex; flex-direction: column; gap: 4px; }
        .user-info .u-name { font-weight: 600; color: white; }
        .user-info .u-login { font-size: 0.78rem; color: #9ca3af; }
        .badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 8px; font-weight: bold; width: fit-content; }
        .badge.pending { background: rgba(234, 179, 8, 0.15); color: #eab308; }
        .badge.approved { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
        .action-btns { display: flex; gap: 6px; }
        .act-btn { border: none; padding: 6px 12px; font-size: 0.75rem; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .act-btn.approve { background: #22c55e; color: white; }
        .act-btn.block { background: #ef4444; color: white; }
    </style>
</head>
<body>

    <!-- OVERLAY AUTHENTIFICATION (LOGIN / REGISTER) -->
    <div class="auth-overlay" id="authOverlay">
        <!-- FORMULAIRE CONNEXION -->
        <div class="auth-box" id="loginBox">
            <h2>Connexion Système</h2>
            <p>Accède à ton instance sécurisée Lou Tsanta</p>
            <div class="input-group"><input type="text" id="loginUser" placeholder="Identifiant"></div>
            <div class="input-group"><input type="password" id="loginPass" placeholder="Mot de passe"></div>
            <button class="auth-btn" onclick="soumettreConnexion()">Se connecter</button>
            <span class="switch-link" onclick="basculerAuth(true)">Créer un nouveau compte</span>
        </div>
        
        <!-- FORMULAIRE INSCRIPTION -->
        <div class="auth-box" id="registerBox" style="display: none;">
            <h2>Créer un compte</h2>
            <p>Remplis les détails. Tsanta devra valider ton accès.</p>
            <div class="input-group"><input type="text" id="regName" placeholder="Ton Nom Complet (Affichage)"></div>
            <div class="input-group"><input type="text" id="regUser" placeholder="Choisis un Identifiant"></div>
            <div class="input-group"><input type="password" id="regPass" placeholder="Choisis un Mot de passe"></div>
            <button class="auth-btn" onclick="soumettreInscription()">Demander l'accès</button>
            <span class="switch-link" onclick="basculerAuth(false)">J'ai déjà un compte</span>
        </div>
    </div>

    <!-- MAIN CONTAINER -->
    <div class="chat-container">
        <div class="header">
            <div class="header-titles">
                <div class="header-main">
                    <span class="status-dot"></span>
                    <h1 id="appTitle">Lou Tsanta</h1>
                </div>
                <div class="author">Par FIDIMANANTSOA Tsantaniaina</div>
            </div>
            <div class="header-actions">
                <button class="nav-btn" id="adminToggleBtn" style="display:none;" onclick="basculerVueAdmin()">Panel Admin</button>
                <button class="nav-btn" onclick="deconnexion()">Déconnexion</button>
            </div>
        </div>
        
        <!-- VUE DISCUSSION -->
        <div class="chat-box" id="chatBox"></div>
        <div class="input-container" id="inputContainer">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Pose ta question..." onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">▲</button>
            </div>
        </div>

        <!-- VUE ADMIN PANEL (GESTION DES COMPTES) -->
        <div class="admin-panel" id="adminPanel">
            <h2>Gestion des Demandes d'Accès</h2>
            <div id="usersList"></div>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];
        let sessionUtilisateur = null;
        let vueAdminActive = false;

        marked.setOptions({ breaks: true, gfm: true });

        // Configuration des clés API Groq obfuscées
        const PARTIE_A = ["gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosqjue", "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"];
        const PARTIE_B = ["WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq", "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"];
        const LISTE_CLES = PARTIE_A.map((p, i) => p + PARTIE_B[i]);
        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA d'élite créée par FIDIMANANTSOA Tsantaniaina, élève en Première S au Lycée Privé Les Dauphins. Tu réponds de manière experte et concise.";

        // VÉRIFICATION AUTOMATIQUE AU CHARGEMENT (Souvenir du nom / de la session)
        window.onload = function() {
            const savedSession = localStorage.getItem('lou_tsanta_session');
            if (savedSession) {
                sessionUtilisateur = JSON.parse(savedSession);
                masquerAuthEtDemarrer();
            }
        };

        function basculerAuth(versRegistre) {
            document.getElementById('loginBox').style.display = versRegistre ? 'none' : 'block';
            document.getElementById('registerBox').style.display = versRegistre ? 'block' : 'none';
        }

        async function soumettreConnexion() {
            const user = document.getElementById('loginUser').value.trim();
            const pass = document.getElementById('loginPass').value.trim();
            if(!user || !pass) return alert("Remplis tous les champs.");

            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: user, password: pass})
            });
            const data = await res.json();
            
            if (data.success) {
                sessionUtilisateur = data.user;
                // Sauvegarde persistante dans le navigateur (ne demande plus le nom le lendemain)
                localStorage.setItem('lou_tsanta_session', JSON.stringify(sessionUtilisateur));
                masquerAuthEtDemarrer();
            } else {
                alert(data.message);
            }
        }

        async function soumettreInscription() {
            const name = document.getElementById('regName').value.trim();
            const user = document.getElementById('regUser').value.trim();
            const pass = document.getElementById('regPass').value.trim();
            if(!name || !user || !pass) return alert("Remplis tous les champs.");

            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, username: user, password: pass})
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) basculerAuth(false);
        }

        function masquerAuthEtDemarrer() {
            document.getElementById('authOverlay').style.display = 'none';
            if (sessionUtilisateur.username === 'admin') {
                document.getElementById('adminToggleBtn').style.style.display = 'block';
            }
            document.getElementById('chatBox').innerHTML = "";
            const welcomeText = `Bonjour **${sessionUtilisateur.name}** ! Je suis **Lou Tsanta**, ravi de te revoir sur ton espace sécurisé. Prêt à travailler ? ⚡`;
            afficherMessage("assistant", welcomeText);
        }

        function deconnexion() {
            localStorage.removeItem('lou_tsanta_session');
            sessionUtilisateur = null;
            location.reload();
        }

        // ==========================================
        # SECTION FONCTIONNALITÉS ADMIN (GESTION ACCÈS)
        // ==========================================
        async function basculerVueAdmin() {
            vueAdminActive = !vueAdminActive;
            if (vueAdminActive) {
                document.getElementById('chatBox').style.display = 'none';
                document.getElementById('inputContainer').style.display = 'none';
                document.getElementById('adminPanel').style.display = 'block';
                document.getElementById('adminToggleBtn').textContent = "Ouvrir le Chat";
                chargerListeUtilisateurs();
            } else {
                document.getElementById('chatBox').style.display = 'flex';
                document.getElementById('inputContainer').style.display = 'block';
                document.getElementById('adminPanel').style.display = 'none';
                document.getElementById('adminToggleBtn').textContent = "Panel Admin";
            }
        }

        async function chargerListeUtilisateurs() {
            const res = await fetch('/api/admin/users');
            const users = await res.json();
            const container = document.getElementById('usersList');
            container.innerHTML = "";
            
            users.forEach(u => {
                if(u.username === 'admin') return;
                const statusBadge = u.is_approved ? '<span class="badge approved">Validé</span>' : '<span class="badge pending">En attente</span>';
                const actionBtn = u.is_approved ? 
                    `<button class="act-btn block" onclick="modifierStatut(${u.id}, 0)">Bloquer</button>` : 
                    `<button class="act-btn approve" onclick="modifierStatut(${u.id}, 1)">Approuver</button>`;

                container.innerHTML += `
                    <div class="user-row">
                        <div class="user-info">
                            <span class="u-name">${u.name}</span>
                            <span class="u-login">ID : ${u.username} | Status: ${statusBadge}</span>
                        </div>
                        <div class="action-btns">${actionBtn}</div>
                    </div>`;
            });
        }

        async function modifierStatut(userId, statut) {
            await fetch('/api/admin/status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: userId, is_approved: statut})
            });
            chargerListeUtilisateurs();
        }

        // ==========================================
        # MOTEUR DE CHAT ET APPELS API
        // ==========================================
        function executerCopieMessage(b) {
            const txt = b.closest('.msg').getAttribute('data-raw');
            navigator.clipboard.writeText(txt);
            b.textContent = "✓ Copié !"; setTimeout(() => { b.textContent = "📋 Copier"; }, 2000);
        }

        function afficherMessage(role, contenu) {
            const box = document.getElementById('chatBox');
            const div = document.createElement('div');
            if (role === "user") {
                div.className = 'msg user'; div.textContent = contenu;
            } else {
                div.className = 'msg bot'; div.setAttribute('data-raw', contenu);
                const c = document.createElement('div'); c.innerHTML = marked.parse(contenu); div.appendChild(c);
                const a = document.createElement('div'); a.className = 'msg-actions'; a.innerHTML = `<button class="copy-btn" onclick="executerCopieMessage(this)">📋 Copier</button>`; div.appendChild(a);
            }
            box.appendChild(div); box.scrollTop = box.scrollHeight;
        }

        async function appelerGroqDirect(payload) {
            const url = "https://api.groq.com/openai/v1/chat/completions";
            for (let i = 0; i < LISTE_CLES.length; i++) {
                try {
                    const response = await fetch(url, {
                        method: "POST",
                        headers: {"Authorization": `Bearer ${LISTE_CLES[i].trim()}`, "Content-Type": "application/json"},
                        body: JSON.stringify(payload)
                    });
                    if (response.status === 200) {
                        const resData = await response.json();
                        return { succes: true, data: resData.choices[0].message.content };
                    }
                } catch (e) {}
            }
            return { succes: false };
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;

            afficherMessage("user", message);
            historiqueMessages.push({"role": "user", "content": message});
            input.value = '';
            
            const loadingId = "loading_" + Date.now();
            document.getElementById('chatBox').innerHTML += `<div class="msg bot loading-msg" id="${loadingId}" style="display:flex;"><div class="spinner"></div>Lou Tsanta réfléchit...</div>`;
            document.getElementById('chatBox').scrollTop = document.getElementById('chatBox').scrollHeight;

            const payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": PROMPT_SYSTEME}, ...historiqueMessages.slice(-6)]
            };

            const resultat = await appelerGroqDirect(payload);
            const loadingEl = document.getElementById(loadingId); if (loadingEl) loadingEl.remove();

            if (resultat.succes) {
                afficherMessage("assistant", resultat.data);
                historiqueMessages.push({"role": "assistant", "content": resultat.data});
            } else {
                document.getElementById('chatBox').innerHTML += `<div class="msg bot">❌ Erreur API. Réessaie dans un instant.</div>`;
            }
            document.getElementById('chatBox').scrollTop = document.getElementById('chatBox').scrollHeight;
        }
    </script>
</body>
</html>
"""

# ==========================================
# GESTION DES ROUTES FLASK ROUTING & ENDPOINTS API
# ==========================================
@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE)

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, name, is_approved) VALUES (?, ?, ?, 0)",
                       (data['username'], data['password'], data['name']))
        conn.commit()
        return jsonify({"success": True, "message": "Demande de compte envoyée ! Attends la validation de Tsanta."})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Cet identifiant existe déjà."})
    finally:
        conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, name, is_approved FROM users WHERE username = ? AND password = ?", 
                   (data['username'], data['password']))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        if user[3] == 1: # Si is_approved vaut 1
            return jsonify({"success": True, "user": {"id": user[0], "username": user[1], "name": user[2]}})
            
        return jsonify({"success": False, "message": "❌ Ton compte n'a pas encore été validé par Tsanta."})
    return jsonify({"success": False, "message": "Identifiant ou mot de passe incorrect."})

@app.route("/api/admin/users", methods=["GET"])
def admin_get_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, name, is_approved FROM users")
    users = [{"id": r[0], "username": r[1], "name": r[2], "is_approved": r[3]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route("/api/admin/status", methods=["POST"])
def admin_set_status():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = ? WHERE id = ?", (data['is_approved'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
