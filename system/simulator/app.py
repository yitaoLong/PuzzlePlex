from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time
from threading import Thread, Event
import webbrowser
import socket

app = Flask(__name__)
socketio = SocketIO(app)

# Chat storage
rooms = None
# statistics storage
globalStats = None
# puzzle name
puzzle_name = None

# Add these lines
stop_event = Event()
server_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    return jsonify(rooms)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(globalStats)

@app.route('/api/puzzle', methods=['GET'])
def get_puzzle():
    return jsonify(puzzle_name)

def get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]

def run_web_ui(chat_storage, stats_storage, name):
    global rooms, globalStats, puzzle_name, server_thread, stop_event
    rooms = chat_storage
    globalStats = stats_storage
    puzzle_name = name
    stop_event.clear()
    
    port = get_free_port()
    
    def run_server():
        socketio.run(app, debug=False, use_reloader=False, port=port)
    
    server_thread = Thread(target=run_server)
    server_thread.daemon = True  # Set the thread as a daemon
    server_thread.start()
    
    # Wait a bit for the server to start
    time.sleep(1)
    
    # Open the web browser
    webbrowser.open(f'http://127.0.0.1:{port}')

def send_ui_message(role, message):
    for index in range(len(rooms)):
        if rooms[index]['type'] == role:
            rooms[index]['messages'].append(message)
            socketio.emit('new_message', {'receiver': role, 'message': message}, namespace='/')
            break

def send_stats(role, value):
    for index in range(len(globalStats)):
        if globalStats[index]['type'] == role:
            globalStats[index]['value'] = value
            break
    socketio.emit('stats_update', globalStats)

def stop_web_ui():
    global stop_event, server_thread
    stop_event.set()
    if server_thread:
        server_thread.join(timeout=5)  # Wait for up to 5 seconds for the thread to finish