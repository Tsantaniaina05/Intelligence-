import os
import sqlite3
import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Emplacement de la base de données (Adapté pour Render)
if os.path.exists("/opt/render/project/src"):
    DB_FILE = "/tmp/database.db"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_FILE = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # PARAMÈTRES PAR DÉFAUT : Identifiant/Mot de passe = 038mj000233 | Nom = Tsanta
    cursor.execute("SELECT * FROM users WHERE username = '038mj000233'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, name, is_approved) VALUES ('038mj000233', '038mj000233', 'Tsanta', 1)")
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"⚠️ Erreur SQLite : {e}")

# ========================================================
# INTERFACE CORRIGÉE POUR L'AFFICHAGE DU CLAVIER MOBILE
# ========================================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Lou Tsanta — Cloud Auth</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        
        /* Correction clavier : Changement de height en min-height et suppression du overflow strict sur le body */
        body { 
            background-color: #080a0f; 
            color: #f1f5f9; 
            display: flex; 
            justify-content: center; 
            min-height: 100vh; 
            min-height: 100dvh; 
        }
        
        /* Conteneur principal flexible */
        .chat-container { 
            width: 100%; 
            max-width: 850px; 
            display: flex; 
            flex-direction: column; 
            height: 100vh;
            height: 100dvh;
            background: #0f111a; 
            position: relative; 
            border-left: 1px solid rgba(255, 46, 99, 0.08); 
            border-right: 1px solid rgba(255, 46, 99, 0.08);
        }

        /* Correction overlay : fixed au lieu de absolute pour s'adapter au redimensionnement du clavier */
        .auth-overlay {
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: #080a0f;
            z-index: 100; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 20px;
            overflow-y: auto; /* Permet de défiler si le clavier prend trop de place */
        }
        
        .auth-box {
            background: #161925; 
            border: 1px solid rgba(255, 46, 99, 0.25); 
            box-shadow: 0 0 30px rgba(255, 46, 99, 0.15);
            padding: 30px; 
            border-radius: 24px; 
            width: 100%; 
            max-width: 400px; 
            text-align: center;
            margin: auto; /* Centre verticalement dans l'overlay déroulant */
        }
        
        .auth-box h2 { font-size: 1.4rem; color: #ffffff; margin-bottom: 8px; }
        .auth-box p { font-size: 0.85rem; color: #9ca3af; margin-bottom: 20px; }
        
        .form-group { text-align: left; margin-bottom: 14px; }
        .form-group label { display: block; font-size: 0.78rem; color: #ff2e63; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; }
        .input-control { width: 100%; background: #080a0f; border: 1px solid rgba(255, 46, 99, 0.2); border-radius: 12px; padding: 12px 16px; color: white; outline: none; font-size: 0.95rem; }
        
        .auth-btn { background: linear-gradient(135deg, #ff2e63 0%, #b80d57 100%); color: white; border: none; padding: 14px; border-radius: 12px; cursor: pointer; font-weight: 600; width: 100%; margin-top: 10px; font-size: 0.95rem; }
        .switch-btn { background: transparent; border: none; color: #ff2e63; font-size: 0.85rem; cursor: pointer; margin-top: 18px; text-decoration: underline; width: 100%; padding: 8px; display: block; }

        .header { padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; background: #0f111a; border-bottom: 1px solid rgba(255, 46, 99, 0.15); z-index: 10; min-height: 75px; }
        .header-main { display: flex; align-items: center; gap: 10px; }
        .header h1 { font-size: 1.25rem; color: #ffffff; font-weight: 700; }
        .status-dot { width: 8px; height: 8px; background-color: #ff2e63; border-radius: 50%; box-shadow: 0 0 10px #ff2e63; }
        .header .author { font-size: 0.72rem; color: #9ca3af; margin-top: 3px; text-transform: uppercase; opacity: 0.7; }
        .header-actions { display: flex; gap: 8px; }
        .nav-btn { background: rgba(255, 46, 99, 0.06); border: 1px solid rgba(255, 46, 99, 0.2); color: #ff2e63; padding: 8px 12px; border-radius: 12px; cursor: pointer; font-size: 0.78rem; font-weight: 600; }

        .chat-box { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; background: linear-gradient(180deg, #0f111a 0%, #090a0f 100%); }
        
        .msg { max-width: 85%; padding: 14px 18px; border-radius: 18px; line-height: 1.6; font-size: 0.96rem; word-wrap: break-word; word-break: break-word; }
        .msg pre { background: #080a0f; padding: 12px; border-radius: 8px; margin: 8px 0; overflow-x: auto; max-width: 100%; border: 1px solid rgba(255, 46, 99, 0.15); }
        .msg code { font-family: 'Courier New', Courier, monospace; font-size: 0.88rem; white-space: pre-wrap; word-break: break-all; }
        
        .user { background: linear-gradient(135deg, #ff2e63 0%, #b80d57 100%); color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #161925; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid rgba(255, 46, 99, 0.1); }

        .input-container { padding: 18px 24px 28px 24px; background: #0f111a; border-top: 1px solid rgba(255, 46, 99, 0.15); }
        .input-wrapper { display: flex; align-items: center; background: #161925; border: 1px solid rgba(255, 46, 99, 0.15); border-radius: 28px; padding: 6px 8px 6px 18px; }
        .input-txt { flex: 1; background: transparent; border: none; color: #ffffff; font-size: 0.98rem; outline: none; padding: 10px 0; }
        .send-btn { background: #ff2e63; color: white; border: none; width: 38px; height: 38px; border-radius: 50%; cursor: pointer; }

        .admin-panel { padding: 24px; overflow-y: auto; flex: 1; display: none; background: #090a0f; }
        .admin-panel h2 { margin-top: 20px; margin-bottom: 15px; color: #fff; font-size: 1.2rem; border-bottom: 2px solid #ff2e63; padding-bottom: 6px; }
        
        .user-row { background: #161925; padding: 14px 20px; border-radius: 14px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .user-info { display: flex; flex-direction: column; gap: 4px; }
        .u-name { font-weight: bold; color: white; }
        .u-login { font-size: 0.8rem; color: #9ca3af; }
        
        .badge { font-size: 0.72rem; padding: 2px 8px; border-radius: 6px; font-weight: bold; }
        .badge.pending { background: rgba(234, 179, 8, 0.15); color: #eab308; }
        .badge.approved { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
        
        .act-btn { border: none; padding: 8px 14px; font-size: 0.78rem; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        .act-btn.approve { background: #22c55e; }
        .act-btn.block { background: #ef4444; }

        .log-item { background: #111420; padding: 12px; border-radius: 10px; border-left: 3px solid #ff2e63; margin-bottom: 8px; font-size: 0.88rem; }
        .log-meta { font-size: 0.75rem; color: #ff2e63; margin-bottom: 4px; font-weight: bold; }
        .log-msg { color: #d1d5db; white-space: pre-wrap; word-break: break-all; }
    </style>
</head>
<body>

    <div class="auth-overlay" id="authOverlay">
        <div class="auth-box" id="loginBox">
            <h2>Connexion Système</h2>
            <p>Accède à ton instance Lou Tsanta</p>
            <form onsubmit="soumettreConnexion(event)">
                <div class="form-group">
                    <label>Identifiant</label>
                    <input type="text" id="loginUser" class="input-control" required placeholder="Ex: rabe">
                </div>
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" id="loginPass" class="input-control" required placeholder="••••••••">
                </div>
                <button type="submit" class="auth-btn">Se connecter</button>
            </form>
            <button type="button" class="switch-btn" onclick="basculerAuth(true, event)">Créer un nouveau compte</button>
        </div>
        
        <div class="auth-box" id="registerBox" style="display: none;">
            <h2>Créer un compte</h2>
            <p>Remplis le formulaire d'accès</p>
            <form onsubmit="soumettreInscription(event)">
                <div class="form-group">
                    <label>Nom complet</label>
                    <input type="text" id="regName" class="input-control" required placeholder="Ex: Rabe">
                </div>
                <div class="form-group">
                    <label>Identifiant désiré</label>
                    <input type="text" id="regUser" class="input-control" required placeholder="Ex: user123">
                </div>
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" id="regPass" class="input-control" required placeholder="••••••••">
                </div>
                <button type="submit" class="auth-btn">Demander l'accès</button>
            </form>
            <button type="button" class="switch-btn" onclick="basculerAuth(false, event)">J'ai déjà un compte</button>
        </div>
    </div>

    <div class="chat-container">
        <div class="header">
            <div class="header-titles">
                <div class="header-main">
                    <span class="status-dot"></span>
                    <h1>Lou Tsanta</h1>
                </div>
                <div class="author">Par FIDIMANANTSOA Tsantaniaina</div>
            </div>
            <div class="header-actions">
                <button type="button" class="nav-btn" id="adminToggleBtn" style="display:none;" onclick="basculerVueAdmin(event)">Panel Privé</button>
                <button type="button" class="nav-btn" onclick="deconnexion(event)">Quitter</button>
            </div>
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-container" id="inputContainer">
            <form onsubmit="sendMessage(event)" class="input-wrapper">
                <input type="text" id="userInput" class="input-txt" placeholder="Pose ta question...">
                <button type="submit" class="send-btn">▲</button>
            </form>
        </div>

        <div class="admin-panel" id="adminPanel">
            <h2>📋 Utilisateurs enregistrés</h2>
            <div id="usersList">Chargement...</div>
            
            <h2>🕒 Historique Général de Recherche</h2>
            <div id="logsList">Chargement...</div>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];
        let sessionUtilisateur = null;
        let vueAdminActive = false;

        marked.setOptions({ breaks: true, gfm: true });

        const PARTIE_A = ["gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosjue", "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"];
        const PARTIE_B = ["WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq", "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"];
        const LISTE_CLES = PARTIE_A.map((p, i) => p + PARTIE_B[i]);
        
        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA d'élite créée par FIDIMANANTSOA Tsantaniaina, un jeune homme qui est un ancien élève de la section scientifique (Terminal D) du Lycée Privé Les Dauphins. Toutes Tes réponses doivent être acompagné des émojies inhabituelles mais qui conviennent aux réponses.";

        window.onload = function() {
            const savedSession = localStorage.getItem('lou_tsanta_render_session');
            if (savedSession) {
                sessionUtilisateur = JSON.parse(savedSession);
                masquerAuthEtDemarrer();
            }
        };

        function basculerAuth(versRegistre, e) {
            if(e) { e.preventDefault(); e.stopPropagation(); }
            document.getElementById('loginBox').style.display = versRegistre ? 'none' : 'block';
            document.getElementById('registerBox').style.display = versRegistre ? 'block' : 'none';
        }

        async function soumettreConnexion(e) {
            if(e) { e.preventDefault(); e.stopPropagation(); }
            const user = document.getElementById('loginUser').value.trim();
            const pass = document.getElementById('loginPass').value.trim();

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: user, password: pass})
                });
                const data = await res.json();
                
                if (data.success) {
                    sessionUtilisateur = data.user;
                    localStorage.setItem('lou_tsanta_render_session', JSON.stringify(sessionUtilisateur));
                    masquerAuthEtDemarrer();
                } else {
                    alert(data.message);
                }
            } catch (err) {
                alert("❌ Connexion impossible.");
            }
        }

        async function soumettreInscription(e) {
            if(e) { e.preventDefault(); e.stopPropagation(); }
            const name = document.getElementById('regName').value.trim();
            const user = document.getElementById('regUser').value.trim();
            const pass = document.getElementById('regPass').value.trim();

            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, username: user, password: pass})
                });
                const data = await res.json();
                alert(data.message);
                if(data.success) basculerAuth(false, null);
            } catch(err) {
                alert("❌ Échec de l'inscription.");
            }
        }

        function masquerAuthEtDemarrer() {
            document.getElementById('authOverlay').style.display = 'none';
            if (sessionUtilisateur.username === '038mj000233') {
                document.getElementById('adminToggleBtn').style.display = 'block';
            }
            document.getElementById('chatBox').innerHTML = "";
            afficherMessage("assistant", `Bonjour **${sessionUtilisateur.name}** ! Base synchronisée. Je t'écoute. ⚡`);
        }

        function deconnexion(e) {
            if(e) e.preventDefault();
            localStorage.clear();
            sessionUtilisateur = null;
            location.reload();
        }

        async function basculerVueAdmin(e) {
            if(e) e.preventDefault();
            vueAdminActive = !vueAdminActive;
            if (vueAdminActive) {
                document.getElementById('chatBox').style.display = 'none';
                document.getElementById('inputContainer').style.display = 'none';
                document.getElementById('adminPanel').style.display = 'block';
                document.getElementById('adminToggleBtn').textContent = "Retour Chat";
                chargerDonneesAdmin();
            } else {
                document.getElementById('chatBox').style.display = 'flex';
                document.getElementById('inputContainer').style.display = 'block';
                document.getElementById('adminPanel').style.display = 'none';
                document.getElementById('adminToggleBtn').textContent = "Panel Privé";
            }
        }

        async function chargerDonneesAdmin() {
            try {
                const resUsers = await fetch('/api/admin/users');
                const users = await resUsers.json();
                const cUsers = document.getElementById('usersList');
                cUsers.innerHTML = "";
                
                users.forEach(u => {
                    if(u.username === '038mj000233') return;
                    const badge = u.is_approved ? '<span class="badge approved">Validé</span>' : '<span class="badge pending">En attente</span>';
                    const button = u.is_approved ? 
                        `<button type="button" class="act-btn block" onclick="modifierStatut(${u.id}, 0)">Bloquer</button>` : 
                        `<button type="button" class="act-btn approve" onclick="modifierStatut(${u.id}, 1)">Approuver</button>`;

                    cUsers.innerHTML += `
                        <div class="user-row">
                            <div class="user-info">
                                <span class="u-name">${u.name}</span>
                                <span class="u-login">ID : ${u.username} | ${badge}</span>
                            </div>
                            <div>${button}</div>
                        </div>`;
                });

                const resLogs = await fetch('/api/admin/logs');
                const logs = await resLogs.json();
                const cLogs = document.getElementById('logsList');
                cLogs.innerHTML = logs.length === 0 ? "<p style='color: #4b5563;'>Aucun historique.</p>" : "";
                
                logs.forEach(l => {
                    cLogs.innerHTML += `
                        <div class="log-item">
                            <div class="log-meta">👤 ${l.username} • 📅 ${l.timestamp}</div>
                            <div class="log-msg">${l.message}</div>
                        </div>`;
                });
            } catch (err) {}
        }

        async function modifierStatut(userId, statut) {
            await fetch('/api/admin/status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: userId, is_approved: statut})
            });
            chargerDonneesAdmin();
        }

        function afficherMessage(role, contenu) {
            const box = document.getElementById('chatBox');
            const div = document.createElement('div');
            div.className = (role === "user") ? 'msg user' : 'msg bot';
            if (role === "user") {
                div.textContent = contenu;
            } else {
                div.innerHTML = marked.parse(contenu);
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

        async function sendMessage(e) {
            if(e) { e.preventDefault(); e.stopPropagation(); }
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;

            afficherMessage("user", message);
            historiqueMessages.push({"role": "user", "content": message});
            input.value = '';

            try {
                fetch('/api/log/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: sessionUtilisateur.username, message: message})
                });
            } catch(e) {}

            const payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": PROMPT_SYSTEME}, ...historiqueMessages.slice(-6)]
            };

            const resultat = await appelerGroqDirect(payload);
            if (resultat.succes) {
                afficherMessage("assistant", resultat.data);
                historiqueMessages.push({"role": "assistant", "content": resultat.data});
            } else {
                afficherMessage("assistant", "❌ Impossible de joindre l'API.");
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# ENDPOINTS BACKEND FLASK
# ==========================================
@app.route("/")
def home():
    try:
        init_db()
    except:
        pass
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
        return jsonify({"success": True, "message": "Inscription enregistrée. En attente de validation."})
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
        if user[3] == 1:
            return jsonify({"success": True, "user": {"id": user[0], "username": user[1], "name": user[2]}})
        return jsonify({"success": False, "message": "🔒 Compte en attente de validation."})
    return jsonify({"success": False, "message": "Identifiant ou mot de passe invalide."})

@app.route("/api/log/search", methods=["POST"])
def save_search_log():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute("INSERT INTO logs (username, message, timestamp) VALUES (?, ?, ?)",
                   (data['username'], data['message'], now))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/users", methods=["GET"])
def admin_get_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, name, is_approved FROM users")
    users = [{"id": r[0], "username": r[1], "name": r[2], "is_approved": r[3]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route("/api/admin/logs", methods=["GET"])
def admin_get_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM logs ORDER BY id DESC")
    logs = [{"username": r[0], "message": r[1], "timestamp": r[2]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(logs)

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
    app.run(host="0.0.0.0", port=port)
