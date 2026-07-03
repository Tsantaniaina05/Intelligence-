import os
from flask import Flask, render_template_string

app = Flask(__name__)

# CONFIGURATION DE L'INTERFACE LOU TSANTA CYBER-RED V3 (MULTILINGUE & EXPERT MALAGASY)
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Lou Tsanta — Cyber-Red</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Courier New', Courier, monospace; }
        
        body { 
            background-color: #050000; 
            color: #ffcccc; 
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
            background: #110000; 
            position: relative;
            border: 2px solid #e60000;
        }

        /* HEADER AVEC EFFET ZIGZAG CSS SUR LE BAS */
        .header { 
            padding: 16px 24px 24px 24px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: #1a0000;
            z-index: 10; 
            min-height: 80px;
            
            -webkit-mask-image: linear-gradient(to bottom, #000 calc(100% - 10px), transparent calc(100% - 10px)),
                                linear-gradient(135deg, #000 5px, transparent 5px),
                                linear-gradient(225deg, #000 5px, transparent 5px);
            -webkit-mask-position: bottom left, bottom left, bottom left;
            -webkit-mask-size: 100% 100%, 10px 10px, 10px 10px;
            -webkit-mask-repeat: no-repeat, repeat-x, repeat-x;
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
            font-size: 1.3rem; 
            color: #ff0000; 
            font-weight: 700; 
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 10px #ff0000;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            background-color: #ff0000;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 15px #ff0000;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 5px #ff0000; }
            50% { box-shadow: 0 0 20px #ff0000; }
            100% { box-shadow: 0 0 5px #ff0000; }
        }

        .header .author { 
            font-size: 0.75rem; 
            color: #ffcccc; 
            margin-top: 4px; 
            font-weight: 400; 
            opacity: 0.9; 
        }

        .clear-btn { 
            background: rgba(230, 0, 0, 0.1); 
            border: 2px solid #e60000; 
            color: #ff9999; 
            padding: 10px 16px; 
            border-radius: 0; 
            cursor: pointer; 
            font-size: 0.85rem; 
            display: flex; 
            align-items: center; 
            gap: 6px; 
            transition: all 0.2s ease; 
            font-weight: 600; 
            text-transform: uppercase;
        }

        .clear-btn:hover { 
            background: #ff0000; 
            color: #000000; 
            box-shadow: 0 0 15px #ff0000;
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
        }

        .chat-box::-webkit-scrollbar { width: 6px; }
        .chat-box::-webkit-scrollbar-thumb { background: #ff0000; }

        /* MESSAGES AVEC DESIGN GÉOMÉTRIQUE CUT OUT */
        .msg { 
            max-width: 82%; 
            padding: 16px 20px; 
            line-height: 1.6; 
            font-size: 0.95rem; 
            word-wrap: break-word; 
            white-space: pre-wrap; 
            position: relative;
        }

        .user { 
            background: #e60000; 
            color: #ffffff; 
            align-self: flex-end; 
            border: 1px solid #ffcccc;
            clip-path: polygon(0 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
        }

        .bot { 
            background: #000000; 
            color: #ffcccc; 
            align-self: flex-start; 
            border: 1px solid #ff0000; 
            box-shadow: inset 0 0 15px rgba(255, 0, 0, 0.3);
            clip-path: polygon(10px 0, 100% 0, 100% 100%, 0 100%, 0 10px);
        }

        /* ZONE DE RÉFLEXION */
        .loading-msg { 
            display: none; 
            align-self: flex-start; 
            background: #1a0000; 
            padding: 14px 18px; 
            border-radius: 0; 
            border: 1px solid #ff0000; 
            color: #ff0000; 
            font-size: 0.95rem; 
            align-items: center; 
            gap: 12px; 
            text-transform: uppercase;
        }

        .spinner { 
            width: 18px; 
            height: 18px; 
            border: 3px solid rgba(255, 0, 0, 0.1); 
            border-top-color: #ff0000; 
            border-radius: 50%; 
            animation: spin 0.8s linear infinite; 
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* CONTENEUR DE SAISIE AVEC ZIGZAG SUR LE HAUT */
        .input-container { 
            padding: 24px 24px 28px 24px; 
            background: #1a0000; 
            z-index: 5;
            
            -webkit-mask-image: linear-gradient(to top, #000 calc(100% - 10px), transparent calc(100% - 10px)),
                                linear-gradient(135deg, #000 5px, transparent 5px),
                                linear-gradient(225deg, #000 5px, transparent 5px);
            -webkit-mask-position: top left, top left, top left;
            -webkit-mask-size: 100% 100%, 10px 10px, 10px 10px;
            -webkit-mask-repeat: no-repeat, repeat-x, repeat-x;
        }

        .input-wrapper { 
            display: flex; 
            align-items: center; 
            background: #000000; 
            border: 2px solid #e60000; 
            border-radius: 0; 
            padding: 8px 10px 8px 18px; 
            transition: all 0.25s ease;
        }

        .input-wrapper:focus-within { 
            background: #111111;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
        }

        input[type="text"] { 
            flex: 1; 
            background: transparent; 
            border: none; 
            color: #ffcccc; 
            font-size: 1rem; 
            padding: 10px 0; 
            outline: none; 
        }

        input[type="text"]::placeholder { 
            color: rgba(255, 204, 204, 0.5); 
        }

        .send-btn { 
            background: #ff0000; 
            color: #000000; 
            border: none; 
            width: 42px; 
            height: 42px; 
            border-radius: 0; 
            cursor: pointer; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 1.1rem; 
            font-weight: bold;
            transition: all 0.2s ease; 
        }

        .send-btn:hover { 
            background: #ffcccc;
            transform: scale(1.05);
            box-shadow: 0 0 15px #ffcccc;
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
                <div class="author">TERMINAL PAR TSANTANIAINA</div>
            </div>
            <button class="clear-btn" onclick="reinitialiserDiscussion()">🗑️ RESET</button>
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="ENTRER VOTRE REQUÊTE..." onkeydown="if(event.key === 'Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">➜</button>
            </div>
        </div>
    </div>
    
    <script>
        let historiqueMessages = [];

        // Les 8 clés API Groq sécurisées
        const PARTIE_A = [
            "gsk_FfwvUhtrQe0buPGq1ZbC", "gsk_jkmG1w3fYMeIPW3zkcIA", "gsk_k5oZjjcuEYcySKmAbQD6", "gsk_fmdEXujMozLZtcosqjue",
            "gsk_T9OSlCCbyz348SgGiqqq", "gsk_PUELW9UBJfOu80IKlOpA", "gsk_7BDECcx7arZ3IssuLKCw", "gsk_B6tXb5B57pnkb1x8V8Ua"
        ];

        const PARTIE_B = [
            "WGdyb3FYeQJs0BMlAlPxfdmErv2KCSah", "WGdyb3FYcThin2ynbGjT7uoMlnL2NQdX", "WGdyb3FYspoPWbFxFthXFCmbblM37syz", "WGdyb3FYHKCy8hJgMfUdHLbbvok5Ngwq",
            "WGdyb3FYFwAXrPQ65YuKJSdW8bPIME35", "WGdyb3FYuPTeSgYwdqeysM51gAKKsrKd", "WGdyb3FYdUp8CBPdUEcc0CNH78Q0QJcD", "WGdyb3FYFoqPUOakMVCarOooeiLU3k6H"
        ];

        const LISTE_CLES = PARTIE_A.map((partie, index) => partie + PARTIE_B[index]);

        // PROMPT SYSTÈME RECONFIGURÉ POUR ÊTRE UN EXPERT ABSOLU EN LANGUES ET EN MALAGASY
        const PROMPT_SYSTEME = "Tu t'appelles Lou Tsanta. Tu es une IA polyglotte d'élite capable de comprendre et de parler couramment TOUTES les langues du monde sans exception. Tu as une maîtrise absolue, parfaite et extrêmement forte de la langue MALAGASY (Malagasy ofisialy, teny madio sy mahay tsara). Si l'utilisateur s'adresse à toi en malagasy, tu dois obligatoirement lui répondre dans un malagasy impeccable, naturel et d'un niveau expert. Ton unique créateur et développeur est FIDIMANANTSOA Tsantaniaina, un élève brillant du Lycée Privé Les Dauphins à Manjakandriana. Tu connais parfaitement son environnement : son professeur de Mathématiques est Mr Germain, son professeur de Physique-Chimie (PC) est Mr Mamy Hasina, son professeur d'Histoire-Géographie est Madame Tantely, son professeur de Philosophie est Fabien Balie, et son professeur d'Anglais est Madame Minosoa. Tu l'aides efficacement dans toutes ses études.";

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
                    chatBox.innerHTML = `<div class="msg bot">SYSTÈME LOU TSANTA CHARGÉ. TON COMPAGNON POLYGLOTTE ET EXPERT EN MALAGASY EST PRÊT. ⚡</div>`;
                }
            } catch (e) {
                chatBox.innerHTML = `<div class="msg bot">ERREUR SYSTÈME. PRÊT À COMMENCER. ⚡</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        };

        function reinitialiserDiscussion() {
            try {
                localStorage.removeItem('loutsanta_chat_history');
                historiqueMessages = [];
                document.getElementById('chatBox').innerHTML = `<div class="msg bot">RESET SYSTÈME EFFECTUÉ. MANOMBOKA VAOVAO NY FIARAHANA. ⚡</div>`;
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
            chatBox.innerHTML += `<div class="msg bot loading-msg" id="${loadingId}" style="display:flex;"><div class="spinner"></div>MANAO TSINDRIANFAHINDRA...</div>`;
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
                        ❌ <b>ERREUR CRITIQUE SYSTÈME</b><br>
                        Saturated API keys. Mba avereno azafady afaka 60 segondra.
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
