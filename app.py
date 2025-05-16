from flask import Flask, request, jsonify
import json

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 👇 Tenta ler o corpo bruto da requisição
        raw_data = request.data.decode('utf-8')
        payload = json.loads(raw_data)

        print("📩 Webhook recebido (raw):", payload)

        # 🟢 Extrair dados básicos
        mensagem_id = payload["data"]["message"]["id"]
        contact_id = payload["data"]["contactId"]

        print(f"🔍 ID da mensagem: {mensagem_id}")
        print(f"👤 contactId: {contact_id}")

        # 1. Buscar conteúdo da mensagem no Digisac
        digisac_url = f"https://bsantos.digisac.biz/api/v1/messages?where[id]={mensagem_id}"
        digisac_headers = {
            "Authorization": f"Bearer {DIGISAC_TOKEN}",
            "Content-Type": "application/json"
        }
        digisac_response = requests.get(digisac_url, headers=digisac_headers)
        digisac_response.raise_for_status()
        mensagem_detalhada = digisac_response.json()
        texto = mensagem_detalhada["data"][0].get("text", "")

        if not texto:
            return jsonify({"error": "Mensagem sem texto"}), 400

        print(f"💬 Texto original: {texto}")

        # 2. Enviar texto para o ChatGPT
        openai_payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Você é um atendente simpático do outlet Só Marcas."},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.7
        }
        openai_headers = {
            "Authorization": f"Bearer {OPENAI_TOKEN}",
            "Content-Type": "application/json"
        }
        gpt_response = requests.post("https://api.openai.com/v1/chat/completions", headers=openai_headers, json=openai_payload)
        gpt_response.raise_for_status()
        resposta = gpt_response.json()["choices"][0]["message"]["content"]

        print("🤖 Resposta do ChatGPT:", resposta)

        # 3. Enviar resposta para o cliente via Digisac
        envio_digisac = {
            "text": resposta,
            "type": "chat",
            "contactId": contact_id,
            "origin": "bot"
        }
        envio_resposta = requests.post("https://bsantos.digisac.biz/api/v1/messages", headers=digisac_headers, json=envio_digisac)
        envio_resposta.raise_for_status()
        print("📤 Resposta enviada para o cliente com sucesso.")

        return jsonify({
            "status": "mensagem respondida",
            "contactId": contact_id,
            "pergunta": texto,
            "resposta": resposta
        }), 200

    except Exception as e:
        print("❌ Erro geral:", str(e))
        return jsonify({"error": "Falha no processo", "detalhe": str(e)}), 500

