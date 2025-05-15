from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Servidor Flask ativo!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📩 Webhook recebido:", data)
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)
