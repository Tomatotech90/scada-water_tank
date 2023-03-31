from flask import Flask, request, jsonify, send_from_directory
from pymodbus.client.sync import ModbusTcpClient

app = Flask(__name__)

modbus_server_ip = "127.0.0.1"  # Change this to your Modbus server IP address
modbus_server_port = 502  # Change this to your Modbus server port number
client = ModbusTcpClient(modbus_server_ip, port=modbus_server_port)


@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('static', 'dashboard.html')


@app.route('/api/tank_levels', methods=['GET'])
def get_tank_levels():
    response = client.read_holding_registers(0, 6)
    if response.isError():
        return jsonify(error=str(response)), 500
    return jsonify(tank_levels=response.registers)


@app.route('/api/add_water', methods=['POST'])
def add_water():
    tank_id = int(request.form.get('tank_id'))
    amount = int(request.form.get('amount'))
    current_level = client.read_holding_registers(tank_id, 1).registers[0]
    new_level = min(current_level + amount, 10)
    client.write_register(tank_id, new_level)
    return jsonify(success=True)


@app.route('/api/discharge_water', methods=['POST'])
def discharge_water():
    tank_id = int(request.form.get('tank_id'))
    amount = int(request.form.get('amount'))
    current_level = client.read_holding_registers(tank_id, 1).registers[0]
    new_level = max(current_level - amount, 0)
    client.write_register(tank_id, new_level)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Change this to your desired IP address and port number
