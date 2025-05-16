@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = json.loads(request.data.decode("utf-8"))
        text = payload["data"]["message"]["text"]
        contact_id = payload["data"]["contactId"]

        # Enviar para OpenAI
        resposta = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "Você é um atendente simpático do outlet Só Marcas."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.7
            }
        ).json()["choices"][0]["message"]["content"]

        # Enviar para Digisac
        requests.post(
            "https://bsantos.digisac.biz/api/v1/messages",
            headers={
                "Authorization": f"Bearer {DIGISAC_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "text": resposta,
                "type": "chat",
                "contactId": contact_id,
                "origin": "bot"
            }
        )

        # Armazenar no log
        logs.append({"texto": text, "resposta": resposta})
        if len(logs) > 20:
            logs.pop(0)

        return jsonify({
            "status": "ok",
            "entrada": text,
            "resposta": resposta,
            "logs": logs[-10:]  # últimos 10 logs
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



