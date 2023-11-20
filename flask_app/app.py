from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__)
process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_program', methods=['POST'])
def start_program():
    global process
    if process:
        return "Programm bereits gestartet."

    try:
        process = subprocess.Popen(["python3", "/home/owipex/h2o.py"])
        return "Programm gestartet."
    except Exception as e:
        return str(e)

@app.route('/stop_program', methods=['POST'])
def stop_program():
    global process
    if not process:
        return "Programm nicht gestartet."
    try:
        process.terminate()
        process = None
        return "Programm gestoppt."
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, threaded=True)

