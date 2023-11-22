from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import subprocess
import threading

app = Flask(__name__)
socketio = SocketIO(app)
process = None

def emit_log_output():
    global process
    if process is not None:
        for line in iter(process.stdout.readline, b''):
            socketio.emit('log_output', {'data': line.decode('utf-8')})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status_program')
def status_program():
    global process
    if process and process.poll() is None:
        return jsonify({'status': 'running'})
    return jsonify({'status': 'stopped'})

@app.route('/start_program', methods=['POST'])
def start_program():
    global process
    if process:
        return "Programm bereits gestartet."

    try:
        process = subprocess.Popen(["python3", "/home/OWIPEX_V1.0/h2o.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        threading.Thread(target=emit_log_output, daemon=True).start()
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

def auto_start():
    global process
    if process is None:
        process = subprocess.Popen(["python3", "/home/OWIPEX_V1.0/h2o.py"])
        print("Programm automatisch gestartet.")
    else:
        print("Programm läuft bereits.")

if __name__ == '__main__':
    auto_start()  # Automatischer Start des Programms beim Starten der Flask-App
    socketio.run(app, host='0.0.0.0', port=8081)

