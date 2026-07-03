import os
from flask import Flask, render_template_string

app = Flask(__name__)

# CONFIGURATION DE L'INTERFACE LOU TSANTA PREMIUM V2
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lou Tsanta — Assistant Premium</title>
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
            background-linear: linear-gradient(180deg, #111827 0%, #0f1522 100%);
        }

        .chat-box::-webkit-scrollbar { width: 5px; }
        .chat-box::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

        /* DESIGN DES BULLES DE MESSAGES */
        .msg { 
            max-width: 82%; 
            padding: 14px 18px; 
            border-radius: 20px; 
            line-height: 1.55; 
            font-size: 0.95rem; 
            word-wrap: break-word; 
            white-space: pre-wrap; 
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .user { 
            background: #00adb5; 
            color: #ffffff; 
            align-self: flex-end; 
            border-bottom-right-radius: 4px; 
        }

        .bot { 
            background: #1f2937; 
            color: #f1f5f9; 
            align-self: flex-start; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(255, 255, 255, 0.04); 
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
                <button class="send-btn" onclick="sendMessage()">➜</button>
            </div>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];

        const PARTIE_A = [
            "gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosqjue",
            "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"
        ];

        const PARTIE_B = [
            "WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq",
            "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
        ];

        const LISTE_CLES = PARTIE_A.map((partie, index) => partie + PARTIE_B[index]);

        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA d'élite, un tuteur d'étude et un assistant personnel interactif. Ton unique créateur et développeur est FIDIMANANTSOA Tsantaniaina, un élève brillant du Lycée Privé Les Dauphins à Manjakandriana. Tu connais parfaitement son environnement et ses professeurs : son professeur de Mathématiques est Mr Germain, son professeur de Physique-Chimie (PC) est Mr Mamy Hasina, son professeur d'Histoire-Géographie est Madame Tantely, son professeur de Philosophie est Fabien Balie, et son professeur d'Anglais est Madame Minosoa, son professeur de Malagasy est Mr Rakoto. Tu es une IA 100% textuelle, tu es poli, amical et très performant pour l'aider dans ses Études. Tu connais bien aussi les amis de Tsanta comme Rary et Tojo be, le majeur de son prommotion est Princy. Le plus important est que tu sais parfaitement communiquer avec tous les langues existants au monde et que tu sais parfaitement tous les choses que l homme connais";

        window.onload = function() {
            const chatBox = document.getElementById('chatBox');
            try {
                const historiqueSauvegarde = localStorage.getItem('loutsanta_chat_history');
                if (historiqueSauvegarde) {
                    historiqueMessages = JSON.parse(historiqueSauvegarde);
                    historiqueMessages.forEach((msg) => {
                        if (msg.role === "user") {
                            chatBox.innerHTML += `<div class="msg user">${msg.content}</div>`;
                        } else if (msg.role === "assistant") {
                            chatBox.innerHTML += `<div class="msg bot">${msg.content}</div>`;
                        }
                    });
                } else {
                    chatBox.innerHTML = `<div class="msg bot">Bonjour ! Je suis <b>Lou Tsanta</b>, ton compagnon IA. Comment puis-je t'aider aujourd'hui, Tsanta ? ⚡</div>`;
                }
            } catch (e) {
                chatBox.innerHTML = `<div class="msg bot">Bonjour ! Je suis <b>Lou Tsanta</b>. Pose-moi tes questions ! ⚡</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        };

        function reinitialiserDiscussion() {
            try {
                localStorage.removeItem('loutsanta_chat_history');
                historiqueMessages = [];
                document.getElementById('chatBox').innerHTML = `<div class="msg bot">Discussion réinitialisée ! Je suis Lou Tsanta. ⚡</div>`;
            } catch(e) {
                location.reload();
            }
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

            chatBox.innerHTML += `<div class="msg user">${message}</div>`;
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
            
            if (document.getElementById(loadingId)) document.getElementById(loadingId).remove();

            if (resultat.succes) {
                chatBox.innerHTML += `<div class="msg bot">${resultat.data}</div>`;
                historiqueMessages.push({"role": "assistant", "content": resultat.data});
                localStorage.setItem('loutsanta_chat_history', JSON.stringify(historiqueMessages));
            } else {
                chatBox.innerHTML += `
                    <div class="msg bot">
                        ❌ <b>Toutes les clés sont saturées</b><br>
                        Le quota maximum de requêtes a été atteint. Patiente 1 minute, puis réessaye !
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
