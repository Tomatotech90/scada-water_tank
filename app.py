from flask import Flask, render_template, jsonify, request
import threading
import modbus_server

app = Flask(__name__)

# Start the Modbus server in a separate thread
modbus_thread = threading.Thread(target=modbus_server.start_server)
modbus_thread.start()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/get_tank_data')
def get_tank_data():
    return jsonify(modbus_server.tanks)

@app.route('/update_tank_level', methods=['POST'])
def update_tank_level():
    tank_id = request.json.get('tank_id')
    new_level = request.json.get('new_level')
    result = modbus_server.update_tank_level(tank_id, new_level)
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
