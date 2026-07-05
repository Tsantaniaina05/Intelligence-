import os
from flask import Flask, render_template_string

app = Flask(__name__)

# INTERFACE PREMIUM V3 - RED CRIMSON EXPERT EDITION
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lou Tsanta — Assistant Pro Red</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        
        body { 
            background-color: #080a0f; 
            color: #f1f5f9; 
            display: flex; 
            justify-content: center; 
            height: 100vh; 
            height: 100dvh; 
            overflow: hidden; 
        }

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

        /* HEADER DÉCORÉ ULTRA PRO */
        .header { 
            padding: 16px 24px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: rgba(15, 17, 26, 0.85); 
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255, 46, 99, 0.15); 
            z-index: 10; 
            min-height: 75px;
            box-shadow: 0 4px 20px rgba(255, 46, 99, 0.05);
        }

        .header-titles { 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
        }

        .header-main {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header h1 { 
            font-size: 1.25rem; 
            color: #ffffff; 
            font-weight: 700; 
            letter-spacing: -0.3px;
            text-shadow: 0 0 10px rgba(255, 46, 99, 0.3);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #ff2e63;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #ff2e63, 0 0 20px #ff2e63;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        .header .author { 
            font-size: 0.72rem; 
            color: #9ca3af; 
            margin-top: 3px; 
            font-weight: 500; 
            letter-spacing: 0.5px;
            text-transform: uppercase;
            opacity: 0.7; 
        }

        .clear-btn { 
            background: rgba(255, 46, 99, 0.06); 
            border: 1px solid rgba(255, 46, 99, 0.2); 
            color: #ff2e63; 
            padding: 8px 14px; 
            border-radius: 16px; 
            cursor: pointer; 
            font-size: 0.8rem; 
            display: flex; 
            align-items: center; 
            gap: 6px; 
            transition: all 0.25s ease; 
            font-weight: 600; 
        }

        .clear-btn:hover { 
            background: #ff2e63; 
            color: #ffffff; 
            border-color: #ff2e63;
            box-shadow: 0 0 12px rgba(255, 46, 99, 0.4);
        }

        /* ZONE DE DISCUSSION ET PANNEAU DE FOND */
        .chat-box { 
            flex: 1; 
            padding: 24px; 
            overflow-y: auto; 
            display: flex; 
            flex-direction: column; 
            gap: 20px; 
            scroll-behavior: smooth;
            background: linear-gradient(180deg, #0f111a 0%, #090a0f 100%);
        }

        .chat-box::-webkit-scrollbar { width: 5px; }
        .chat-box::-webkit-scrollbar-thumb { background: rgba(255, 46, 99, 0.15); border-radius: 10px; }

        /* DESIGN DES BULLES DE MESSAGES */
        .msg { 
            max-width: 85%; 
            padding: 14px 18px; 
            border-radius: 18px; 
            line-height: 1.6; 
            font-size: 0.96rem; 
            word-wrap: break-word; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }

        .user { 
            background: linear-gradient(135deg, #ff2e63 0%, #b80d57 100%); 
            color: #ffffff; 
            align-self: flex-end; 
            border-bottom-right-radius: 4px; 
            white-space: pre-wrap;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .bot { 
            background: #161925; 
            color: #e2e8f0; 
            align-self: flex-start; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(255, 46, 99, 0.1); 
        }

        /* ISOLATION ET DESIGN DES BLOCS DE CODE (ROUGE / NOIR CYBER) */
        .bot pre {
            background: #080a0f !important;
            border-left: 3px solid #ff2e63 !important;
            border-top: 1px solid rgba(255, 46, 99, 0.15) !important;
            border-right: 1px solid rgba(255, 46, 99, 0.15) !important;
            border-bottom: 1px solid rgba(255, 46, 99, 0.15) !important;
            padding: 14px !important;
            margin: 14px 0 !important;
            overflow-x: auto !important;
            border-radius: 8px !important;
            display: block !important;
            width: 100% !important;
        }

        .bot code {
            font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
            color: #f1f5f9 !important;
            font-size: 0.88rem !important;
            background: transparent !important;
            padding: 0 !important;
        }
        
        /* Code en ligne */
        .bot p code {
            background: #080a0f !important;
            color: #ff2e63 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-weight: 600;
        }

        /* ACTIONS SUR LES MESSAGES (BOUTON COPIER PRO) */
        .msg-actions {
            display: flex;
            justify-content: flex-end;
            margin-top: 10px;
        }

        .copy-btn {
            background: rgba(255, 46, 99, 0.05);
            border: 1px solid rgba(255, 46, 99, 0.2);
            color: #ff2e63;
            padding: 5px 12px;
            font-size: 0.75rem;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .copy-btn:hover {
            background: #ff2e63;
            color: #ffffff;
            box-shadow: 0 0 8px rgba(255, 46, 99, 0.3);
        }

        /* INDIFICATEUR DE RÉFLEXION LOU TSANTA */
        .loading-msg { 
            display: none; 
            align-self: flex-start; 
            background: #161925; 
            padding: 14px 18px; 
            border-radius: 18px; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(255, 46, 99, 0.15); 
            color: #9ca3af; 
            font-size: 0.92rem; 
            align-items: center; 
            gap: 12px; 
        }

        .spinner { 
            width: 16px; 
            height: 16px; 
            border: 2px solid rgba(255, 46, 99, 0.1); 
            border-top-color: #ff2e63; 
            border-radius: 50%; 
            animation: spin 0.8s linear infinite; 
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* DECORATION ZONE DE SAISIE FLOTTANTE */
        .input-container { 
            padding: 18px 24px 28px 24px; 
            background: #0f111a; 
            border-top: 1px solid rgba(255, 46, 99, 0.15); 
        }

        .input-wrapper { 
            display: flex; 
            align-items: center; 
            background: #161925; 
            border: 1px solid rgba(255, 46, 99, 0.15); 
            border-radius: 28px; 
            padding: 6px 8px 6px 18px; 
            transition: all 0.25s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .input-wrapper:focus-within { 
            border-color: #ff2e63; 
            background: #1d2133;
            box-shadow: 0 0 0 3px rgba(255, 46, 99, 0.15);
        }

        input[type="text"] { 
            flex: 1; 
            background: transparent; 
            border: none; 
            color: #ffffff; 
            font-size: 0.98rem; 
            padding: 10px 0; 
            outline: none; 
        }

        input[type="text"]::placeholder { 
            color: #4b5563; 
        }

        /* BOUTON FLÈCHE VERS LE HAUT PARFAITEMENT CENTRÉ */
        .send-btn { 
            background: #ff2e63; 
            color: white; 
            border: none; 
            width: 38px; 
            height: 38px; 
            border-radius: 50%; 
            cursor: pointer; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 0.85rem; 
            padding-bottom: 2px;
            transition: all 0.2s ease; 
            box-shadow: 0 0 10px rgba(255, 46, 99, 0.3);
        }

        .send-btn:hover { 
            background: #ff4777; 
            transform: scale(1.05);
            box-shadow: 0 0 14px rgba(255, 46, 99, 0.5);
        }
        
        .send-btn:active {
            transform: scale(0.95);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <div class="header-titles">
                <div class="header-main">
                    <span class="status-dot"></span>
                    <h1>Lou Tsanta</h1>
                </div>
                <div class="author">Par FIDIMANANTSOA Tsantaniaina</div>
            </div>
            <button class="clear-btn" onclick="reinitialiserDiscussion()">🗑️ Effacer</button>
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Pose ta question à Lou Tsanta..." onkeydown="if(event.key === 'Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">▲</button>
            </div>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];

        marked.setOptions({
            breaks: true,
            gfm: true
        });

        const PARTIE_A = [
            "gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosqjue",
            "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"
        ];

        const PARTIE_B = [
            "WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq",
            "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
        ];

        const LISTE_CLES = PARTIE_A.map((partie, index) => partie + PARTIE_B[index]);

        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA d'élite, un développeur chevronné de niveau légendaire et un tuteur d'étude. Tu as une capacité exceptionnelle pour générer des scripts parfaits et du code propre (Python, Bash, PHP, JS, etc.) sans erreurs. Tu dois obligatoirement utiliser les blocs de code Markdown (avec triple backticks) pour isoler tes codes. Ton unique créateur et développeur est FIDIMANANTSOA Tsantaniaina, un élève brillant du Lycée Privé Les Dauphins à Manjakandriana. Tu connais parfaitement son environnement et ses professeurs : son professeur de Mathématiques est Mr Germain, son professeur de Physique-Chimie (PC) est Mr Mamy Hasina, son professeur d'Histoire-Géographie est Madame Tantely, son professeur de Philosophie est Fabien Balie, et son professeur d'Anglais est Madame Minosoa. Tu es poli, amical et ultra-performant.";

        window.onload = function() {
            try {
                localStorage.clear();
                afficherMessage("assistant", "Bonjour ! Je suis **Lou Tsanta**, ton compagnon IA et expert en programmation. Comment puis-je t'aider aujourd'hui, Tsanta ? ⚡");
            } catch (e) {
                document.getElementById('chatBox').innerHTML = `<div class="msg bot">Bonjour ! Je suis Lou Tsanta. Pose-moi tes questions ! ⚡</div>`;
            }
        };

        function reinitialiserDiscussion() {
            localStorage.clear();
            historiqueMessages = [];
            document.getElementById('chatBox').innerHTML = `<div class="msg bot">Discussion réinitialisée ! Je suis Lou Tsanta. ⚡</div>`;
        }

        function executerCopieMessage(bouton) {
            const conteneur = bouton.closest('.msg');
            const texteBrut = conteneur.getAttribute('data-raw');
            navigator.clipboard.writeText(texteBrut);
            bouton.textContent = "✓ Copié !";
            setTimeout(() => { bouton.textContent = "📋 Copier"; }, 2000);
        }

        function afficherMessage(role, contenu) {
            const chatBox = document.getElementById('chatBox');
            const divMsg = document.createElement('div');
            
            if (role === "user") {
                divMsg.className = 'msg user';
                divMsg.textContent = contenu;
            } else {
                divMsg.className = 'msg bot';
                divMsg.setAttribute('data-raw', contenu);

                const divContenu = document.createElement('div');
                divContenu.innerHTML = marked.parse(contenu);
                divMsg.appendChild(divContenu);

                const divActions = document.createElement('div');
                divActions.className = 'msg-actions';
                divActions.innerHTML = `<button class="copy-btn" onclick="executerCopieMessage(this)">📋 Copier</button>`;
                divMsg.appendChild(divActions);
            }
            
            chatBox.appendChild(divMsg);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function appelerGroqDirect(payload) {
            const url = "https://api.groq.com/openai/v1/chat/completions";
            for (let i = 0; i < LISTE_CLES.length; i++) {
                let key = LISTE_CLES[i];
                try {
                    const response = await fetch(url, {
                        method: "POST",
                        headers: {
                            "Authorization": `Bearer ${key.trim()}`,
                            "Content-Type": "application/json"
                        },
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
            const chatBox = document.getElementById('chatBox');
            const message = input.value.trim();
            if (!message) return;

            afficherMessage("user", message);
            historiqueMessages.push({"role": "user", "content": message});

            input.value = '';
            
            const loadingId = "loading_" + Date.now();
            chatBox.innerHTML += `<div class="msg bot loading-msg" id="${loadingId}" style="display:flex;"><div class="spinner"></div>Lou Tsanta réfléchit...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            // OPTIMISATION ANTI-SATURATION : Historique borné à 6 messages et modèle 8B instantané
            const payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": PROMPT_SYSTEME}, ...historiqueMessages.slice(-6)]
            };

            const resultat = await appelerGroqDirect(payload);
            
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();

            if (resultat.succes) {
                afficherMessage("assistant", resultat.data);
                historiqueMessages.push({"role": "assistant", "content": resultat.data});
            } else {
                chatBox.innerHTML += `
                    <div class="msg bot">
                        ❌ <b>Misy olana ny fifandraisana</b><br>
                        Manandrama indray afaka 60 segondra azafady.
                    </div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_INTERFACE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
