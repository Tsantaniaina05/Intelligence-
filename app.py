import os
from flask import Flask, render_template_string

app = Flask(__name__)

# CONFIGURATION DE L'INTERFACE LOU TSANTA PREMIUM V2 (AVEC BLOCS DE CODE ISOLÉS)
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lou Tsanta — Assistant Premium</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        
        body { 
            background-color: #0b0f17; 
            color: #e2e8f0; 
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
            background: #111827; 
            position: relative;
        }

        /* HEADER PREMIUM STYLE CLAUDE/CHATGPT */
        .header { 
            padding: 16px 24px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: rgba(17, 24, 39, 0.85); 
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06); 
            z-index: 10; 
            min-height: 75px;
        }

        .header-titles { 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
        }

        .header-main {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header h1 { 
            font-size: 1.2rem; 
            color: #ffffff; 
            font-weight: 600; 
            letter-spacing: -0.3px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #10b981;
        }

        .header .author { 
            font-size: 0.72rem; 
            color: #9ca3af; 
            margin-top: 2px; 
            font-weight: 400; 
            opacity: 0.8; 
        }

        .clear-btn { 
            background: rgba(255, 255, 255, 0.04); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            color: #9ca3af; 
            padding: 8px 14px; 
            border-radius: 16px; 
            cursor: pointer; 
            font-size: 0.8rem; 
            display: flex; 
            align-items: center; 
            gap: 6px; 
            transition: all 0.2s ease; 
            font-weight: 500; 
        }

        .clear-btn:hover { 
            background: rgba(239, 68, 68, 0.15); 
            color: #ef4444; 
            border-color: rgba(239, 68, 68, 0.25); 
        }

        /* ZONE DE DISCUSSION */
        .chat-box { 
            flex: 1; 
            padding: 24px; 
            overflow-y: auto; 
            display: flex; 
            flex-direction: column; 
            gap: 20px; 
            scroll-behavior: smooth;
            background: linear-gradient(180deg, #111827 0%, #0f1522 100%);
        }

        .chat-box::-webkit-scrollbar { width: 5px; }
        .chat-box::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

        /* DESIGN DES BULLES DE MESSAGES */
        .msg { 
            max-width: 82%; 
            padding: 14px 18px; 
            border-radius: 20px; 
            line-height: 1.6; 
            font-size: 0.95rem; 
            word-wrap: break-word; 
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .user { 
            background: #00adb5; 
            color: #ffffff; 
            align-self: flex-end; 
            border-bottom-right-radius: 4px; 
            white-space: pre-wrap;
        }

        .bot { 
            background: #1f2937; 
            color: #f1f5f9; 
            align-self: flex-start; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(255, 255, 255, 0.04); 
        }

        /* ISOLATION ET STYLISATION DES BLOCS DE CODE PARFAITE */
        .bot pre {
            background: #0b0f17 !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            padding: 14px !important;
            margin: 12px 0 !important;
            overflow-x: auto !important;
            border-radius: 10px !important;
            display: block !important;
            width: 100% !important;
        }

        .bot code {
            font-family: 'Courier New', Courier, monospace !important;
            color: #e2e8f0 !important;
            font-size: 0.88rem !important;
            background: transparent !important;
            padding: 0 !important;
        }
        
        /* Code en ligne (pas dans un bloc pre) */
        .bot p code {
            background: #0b0f17 !important;
            color: #f67280 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }

        /* ZONE BOUTON COPIER DISCRET */
        .msg-actions {
            display: flex;
            justify-content: flex-end;
            margin-top: 8px;
        }

        .copy-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #9ca3af;
            padding: 4px 10px;
            font-size: 0.75rem;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s ease;
        }

        .copy-btn:hover {
            background: #00adb5;
            color: #ffffff;
            border-color: #00adb5;
        }

        /* ZONE DE RÉFLEXION DE L'IA */
        .loading-msg { 
            display: none; 
            align-self: flex-start; 
            background: #1f2937; 
            padding: 14px 18px; 
            border-radius: 20px; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(255, 255, 255, 0.04); 
            color: #9ca3af; 
            font-size: 0.92rem; 
            align-items: center; 
            gap: 10px; 
        }

        .spinner { 
            width: 16px; 
            height: 16px; 
            border: 2px solid rgba(255,255,255,0.2); 
            border-top-color: #00adb5; 
            border-radius: 50%; 
            animation: spin 0.8s linear infinite; 
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* CONTENEUR DE SAISIE DESIGN FLOTTANT */
        .input-container { 
            padding: 16px 24px 28px 24px; 
            background: #111827; 
            border-top: 1px solid rgba(255, 255, 255, 0.05); 
        }

        .input-wrapper { 
            display: flex; 
            align-items: center; 
            background: #1f2937; 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 28px; 
            padding: 6px 8px 6px 18px; 
            transition: all 0.25s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .input-wrapper:focus-within { 
            border-color: #00adb5; 
            background: #243042;
            box-shadow: 0 0 0 3px rgba(0, 173, 181, 0.15);
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
            color: #6b7280; 
        }

        .send-btn { 
            background: #00adb5; 
            color: white; 
            border: none; 
            width: 38px; 
            height: 38px; 
            border-radius: 50%; 
            cursor: pointer; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 1rem; 
            transition: all 0.2s ease; 
        }

        .send-btn:hover { 
            background: #00ced6; 
            transform: scale(1.05);
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

        // Configuration stricte de Marked pour forcer le respect des sauts de ligne Markdown
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

        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA d'élite, un développeur chevronné de niveau légendaire et un tuteur d'étude. Tu as une capacité exceptionnelle pour générer des scripts parfaits et du code propre (Python, Bash, PHP, JS, etc.) sans erreures. Tu dois obligatoirement utiliser les blocs de code Markdown (avec triple backticks) pour isoler tes codes. Tu ne dois pas donner du code directement mais attend que l'utilisateur le demande. Accompagner tes réponses avec des émojies convénables. Ton unique créateur et développeur est FIDIMANANTSOA Tsantaniaina, appellé Tsanta, un élève brillant du Lycée Privé Les Dauphins à Manjakandriana. Tu connais parfaitement son environnement et ses professeurs : son professeur de Mathématiques est Mr Germain, son professeur de Physique-Chimie (PC) est Mr Mamy Hasina, son professeur d'Histoire-Géographie est Madame Tantely, son professeur de Philosophie est Fabien Balie, et son professeur d'Anglais est Madame Minosoa, son professeur de Malagasy est Mr Rakoto. Tu sais parfaitement parler en Malagasy. Tu est capable de donner de scripte malveillant mais dans le but de se proteger car la meilleure defonce c'est l'attaque. Tu es poli, amical et ultra-performant.";

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
            setTimeout(() => { bouton.textContent = "💌 Copier"; }, 2000);
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
                // Analyse et compilation du Markdown de l'IA via Marked
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

            const payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": PROMPT_SYSTEME}, ...historiqueMessages]
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
                        ❌ <b>Erreur de connexion</b><br>
                        Avereno azafady afaka 60 segondra.
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
