from flask import Flask, request, jsonify, send_from_directory
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

import threading

# Set up Modbus TCP server
holding_register = [0] * 6
store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, holding_register))
context = ModbusServerContext(slaves=store, single=True)

def run_modbus_server():
    StartTcpServer(context, address=("0.0.0.0", 502))

# Run Modbus server in a separate thread
modbus_server_thread = threading.Thread(target=run_modbus_server)
modbus_server_thread.start()

# Set up Flask web server
app = Flask(__name__)

@app.route('/api/get_tank_levels', methods=['GET'])
def get_tank_levels():
    return jsonify(holding_register)

@app.route('/api/add_water', methods=['POST'])
def add_water():
    tank_id = int(request.form.get('tank_id'))
    amount = float(request.form.get('amount'))

    current_level = holding_register[tank_id]
    new_level = min(current_level + amount, 10)  # Ensure the level does not exceed 10
    holding_register[tank_id] = new_level

    return jsonify(success=True)

@app.route('/api/discharge_water', methods=['POST'])
def discharge_water():
    tank_id = int(request.form.get('tank_id'))
    amount = float(request.form.get('amount'))

    current_level = holding_register[tank_id]
    new_level = max(current_level - amount, 0)  # Ensure the level does not go below 0
    holding_register[tank_id] = new_level

    return jsonify(success=True)

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('static', 'dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
