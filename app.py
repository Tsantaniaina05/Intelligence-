import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==========================================
# INTERFACE SÉCURISÉE COMPATIBLE RENDER (SANS SQLITE)
# ==========================================
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lou Tsanta — Superviseur Cloud</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background-color: #080a0f; color: #f1f5f9; display: flex; justify-content: center; height: 100vh; height: 100dvh; overflow: hidden; }
        
        .chat-container { 
            width: 100%; max-width: 850px; display: flex; flex-direction: column; height: 100vh; height: 100dvh; 
            background: #0f111a; position: relative; border-left: 1px solid rgba(255, 46, 99, 0.08); border-right: 1px solid rgba(255, 46, 99, 0.08);
        }

        .header { padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; background: #0f111a; border-bottom: 1px solid rgba(255, 46, 99, 0.15); z-index: 10; min-height: 75px; }
        .header-main { display: flex; align-items: center; gap: 10px; }
        .header h1 { font-size: 1.25rem; color: #ffffff; font-weight: 700; }
        .status-dot { width: 8px; height: 8px; background-color: #ff2e63; border-radius: 50%; box-shadow: 0 0 10px #ff2e63; }
        .header .author { font-size: 0.72rem; color: #9ca3af; margin-top: 3px; text-transform: uppercase; opacity: 0.7; }

        .chat-box { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; background: linear-gradient(180deg, #0f111a 0%, #090a0f 100%); }
        .msg { max-width: 85%; padding: 14px 18px; border-radius: 18px; line-height: 1.6; font-size: 0.96rem; word-wrap: break-word; }
        .user { background: linear-gradient(135deg, #ff2e63 0%, #b80d57 100%); color: #ffffff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .bot { background: #161925; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid rgba(255, 46, 99, 0.1); }

        .input-container { padding: 18px 24px 28px 24px; background: #0f111a; border-top: 1px solid rgba(255, 46, 99, 0.15); }
        .input-wrapper { display: flex; align-items: center; background: #161925; border: 1px solid rgba(255, 46, 99, 0.15); border-radius: 28px; padding: 6px 8px 6px 18px; }
        .input-txt { flex: 1; background: transparent; border: none; color: #ffffff; font-size: 0.98rem; outline: none; padding: 10px 0; }
        .send-btn { background: #ff2e63; color: white; border: none; width: 38px; height: 38px; border-radius: 50%; cursor: pointer; }
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
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-container" id="inputContainer">
            <form onsubmit="sendMessage(event)" class="input-wrapper">
                <input type="text" id="userInput" class="input-txt" placeholder="Pose ta question à Lou Tsanta...">
                <button type="submit" class="send-btn">▲</button>
            </form>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];
        marked.setOptions({ breaks: true, gfm: true });

        const PARTIE_A = ["gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosqjue", "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"];
        const PARTIE_B = ["WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq", "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"];
        const LISTE_CLES = PARTIE_A.map((p, i) => p + PARTIE_B[i]);
        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA d'élite créée par FIDIMANANTSOA Tsantaniaina, élève en Première S au Lycée Privé Les Dauphins.";

        window.onload = function() {
            afficherMessage("assistant", "Bonjour ! Je suis opérationnelle et prête à t'aider. Que puis-je faire pour toi aujourd'hui ? ⚡");
        };

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

            const payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "system", "content": PROMPT_SYSTEME}, ...historiqueMessages.slice(-6)]
            };

            const resultat = await appelerGroqDirect(payload);
            if (resultat.succes) {
                afficherMessage("assistant", resultat.data);
                historiqueMessages.push({"role": "assistant", "content": resultat.data});
            } else {
                afficherMessage("assistant", "❌ Impossible de joindre l'API. Vérifie tes clés Groq.");
            }
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
