from flask import Flask, request, jsonify, send_from_directory
from compiler.compiler import compile_expression, generate_random_expression
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code', '')
    result = compile_expression(code)
    return jsonify(result)

@app.route('/random-expression', methods=['GET'])
def random_expression():
    expr = generate_random_expression()
    return jsonify({"expression": expr})

if __name__ == '__main__':
    app.run(debug=True)
