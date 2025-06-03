from flask import Flask, request, jsonify, send_from_directory
from compiler.compiler import compile_expression, generate_random_expression
import os
import json

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# File to persist history
HISTORY_FILE = 'history.json'

# Load history from file if it exists
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
else:
    history = []

def save_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-100:], f)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code', '').strip()

    if code and code not in history:
        history.append(code)
        if len(history) > 100:
            history.pop(0)
        save_history()

    result = compile_expression(code)
    return jsonify(result)

@app.route('/random-expression', methods=['GET'])
def random_expression():
    expr = generate_random_expression()

    if expr and expr not in history:
        history.append(expr)
        if len(history) > 100:
            history.pop(0)
        save_history()

    return jsonify({"expression": expr})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({"history": history[-20:]})  # Return latest 20

@app.route('/history/<int:index>', methods=['DELETE'])
def delete_history_entry(index):
    if 0 <= index < len(history):
        deleted = history.pop(index)
        save_history()
        return jsonify({"message": "Deleted", "deleted": deleted})
    return jsonify({"error": "Index out of range"}), 400

@app.route('/history', methods=['DELETE'])
def clear_history():
    history.clear()
    save_history()
    return jsonify({"message": "History cleared"})

if __name__ == '__main__':
    app.run(debug=True)
