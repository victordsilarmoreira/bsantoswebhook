from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    print("📩 Dados recebidos:", data)
    return jsonify({"status": "ok", "recebido": data}), 200

if __name__ == '__main__':
    app.run(port=5000)
