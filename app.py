from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Webhook recebido:")
    print(data)

    # Aqui você pode fazer algo com os dados recebidos, como acionar um fluxo
    # ou enviar para outro sistema

    return jsonify({"status": "sucesso", "mensagem": "Webhook processado"}), 200

if __name__ == '__main__':
    app.run(port=5000)

