from flask import Flask, render_template, jsonify, request
import threading
import socket
import struct
import time

app = Flask(__name__)

# Modbus server settings
LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 502
REGISTERS_PER_TANK = 2
NUM_TANKS = 6
STARTING_ADDR = 0x0000

# Tank data
tanks = {}
for i in range(1, NUM_TANKS+1):
    tanks[i] = {
        'level': 0,
        'temperature': 0,
    }

# Modbus server functions
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    server_socket.listen(1)
    print(f'Modbus server listening on {LISTEN_IP}:{LISTEN_PORT}...')

    while True:
        client_socket, address = server_socket.accept()
        print(f'Accepted connection from {address[0]}:{address[1]}')
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket,), daemon=True)
        client_thread.start()

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f'Received data from {client_socket.getpeername()}: {data.hex()}')
            response = process_request(data)
            print(f'Sending response to {client_socket.getpeername()}: {response.hex()}')
            client_socket.sendall(response)
    except Exception as e:
        print(f'Error handling client: {e}')
    finally:
        client_socket.close()

def process_request(request):
    # Parse the request
    transaction_id, protocol_id, length, unit_id, function_code, address, count = struct.unpack('>HHHBBBB', request[:11])
    end_address = address + count - 1

    # Validate the request
    if protocol_id != 0 or length != 6:
        return build_error_response(transaction_id, function_code, 0x01)
    if unit_id != 1:
        return build_error_response(transaction_id, function_code, 0x11)
    if function_code != 0x03 or address > 0xFF or end_address > 0xFF:
        return build_error_response(transaction_id, function_code, 0x02)

    # Build the response
    values = []
    for i in range(address, end_address+1):
        tank_id, register_type = get_register_info(i)
        if tank_id == -1:
            return build_error_response(transaction_id, function_code, 0x02)
        tank = tanks[tank_id]
        if register_type == 'level':
            value = tank['level']
        elif register_type == 'temperature':
            value = tank['temperature']
        values.extend(struct.pack('>H', value))
    response = struct.pack(f'>HHHBBB{len(values)}s', transaction_id, protocol_id, 3+2*count, unit_id, function_code, 2*count, *values)
    return response

def get_register_info(register_address):
    if register_address % REGISTERS_PER_TANK == 0:
        tank_id = register_address // REGISTERS_PER_TANK
        if tank_id < 1 or tank_id > NUM_TANKS:
            return (-1, None)
        register_type = 'level' if (register_address % REGISTERS_PER_TANK) == 0 else 'temperature'
        return (tank_id, register_type)
    else:
        return (-1, None)


# Add water and discharge water routes
@app.route('/add_water', methods=['POST'])
def add_water():
    tank_id = int(request.form['tank_id'])
    amount = int(request.form['amount'])
    if tank_id < 1 or tank_id > NUM_TANKS:
        return jsonify({'status': 'error', 'message': 'Invalid tank ID'})
    tank = tanks[tank_id]
    tank['level'] = min(100, tank['level'] + amount)
    return jsonify({'status': 'success', 'message': f'Added {amount} liters to tank {tank_id}'})

@app.route('/discharge_water', methods=['POST'])
def discharge_water():
    tank_id = int(request.form['tank_id'])
    amount = int(request.form['amount'])
    if tank_id < 1 or tank_id > NUM_TANKS:
        return jsonify({'status': 'error', 'message': 'Invalid tank ID'})
    tank = tanks[tank_id]
    tank['level'] = max(0, tank['level'] - amount)
    return jsonify({'status': 'success', 'message': f'Discharged {amount} liters from tank {tank_id}'})

# Dashboard route
@app.route('/')
def dashboard():
    return render_template('dashboard.html', tanks=tanks)

# Start the modbus server in a new thread
modbus_thread = threading.Thread(target=start_server, daemon=True)
modbus_thread.start()

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
