import socket
import struct
import threading

# Define the tanks and their current water levels
tanks = {
    1: {'level': 0, 'max_level': 100, 'min_level': 0},
    2: {'level': 0, 'max_level': 100, 'min_level': 0},
    3: {'level': 0, 'max_level': 100, 'min_level': 0},
    4: {'level': 0, 'max_level': 100, 'min_level': 0},
    5: {'level': 0, 'max_level': 100, 'min_level': 0},
    6: {'level': 0, 'max_level': 100, 'min_level': 0},
    
}

# Define the Modbus function codes
FC_READ_COILS = 0x01
FC_READ_DISCRETE_INPUTS = 0x02
FC_READ_HOLDING_REGISTERS = 0x03
FC_READ_INPUT_REGISTERS = 0x04
FC_WRITE_SINGLE_COIL = 0x05
FC_WRITE_SINGLE_REGISTER = 0x06
FC_WRITE_MULTIPLE_COILS = 0x0F
FC_WRITE_MULTIPLE_REGISTERS = 0x10

# Define the Modbus exception codes
EX_ILLEGAL_FUNCTION = 0x01
EX_ILLEGAL_DATA_ADDRESS = 0x02
EX_ILLEGAL_DATA_VALUE = 0x03
EX_SERVER_DEVICE_FAILURE = 0x04
EX_ACKNOWLEDGE = 0x05
EX_SERVER_DEVICE_BUSY = 0x06
EX_MEMORY_PARITY_ERROR = 0x08
EX_GATEWAY_PATH_UNAVAILABLE = 0x0A
EX_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0B

# Define the Modbus packet format
MODBUS_PACKET_FORMAT = '>HHHBBH'

# Define the listening IP address and port
LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 502

# Define the Modbus server thread
class ModbusServerThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        while True:
            try:
                # Receive data from the socket
                data = self.sock.recv(1024)
                if not data:
                    break

                # Decode the Modbus request packet
                transaction_id, protocol_id, length, unit_id, function_code, address, quantity = struct.unpack(MODBUS_PACKET_FORMAT, data)

                # Handle the Modbus function code
                if function_code == FC_READ_HOLDING_REGISTERS:
                    # Read the water level from the specified tank
                    if address in tanks:
                        level = tanks[address]['level']
                        max_level = tanks[address]['max_level']
                        min_level = tanks[address]['min_level']
                        response_data = struct.pack('>BBHH', unit_id, FC_READ_HOLDING_REGISTERS, level, max_level)
                    else:
                        response_data = struct.pack('>BB', unit_id, function_code | 0x80) + bytes([EX_ILLEGAL_DATA_ADDRESS])
                elif function_code == FC_WRITE_SINGLE_REGISTER:
                    # Write the water level to the specified tank
                   
                    if address in tanks:
                        level, = struct.unpack('>H', data[6:])
                        if level >= tanks[address]['min_level'] and level <= tanks[address]['max_level']:
                            tanks[address]['level'] = level
                            response_data = struct.pack('>HH', address, level)
                        else:
                            response_data = struct.pack('>BB', unit_id, function_code | 0x80) + bytes([EX_ILLEGAL_DATA_VALUE])
                    else:
                        response_data = struct.pack('>BB', unit_id, function_code | 0x80) + bytes([EX_ILLEGAL_DATA_ADDRESS])
                else:
                    # Return an error for unsupported function codes
                    response_data = struct.pack('>BB', unit_id, function_code | 0x80) + bytes([EX_ILLEGAL_FUNCTION])

                # Encode the Modbus response packet
                response_length = len(response_data) + 2
                response = struct.pack(MODBUS_PACKET_FORMAT, transaction_id, protocol_id, response_length, unit_id, function_code, len(response_data)) + response_data

                # Send the Modbus response packet
                self.sock.sendall(response)
            except Exception as e:
                print('Exception:', e)
                break

        # Close the socket when the thread is finished
        self.sock.close()

# Create the Modbus server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((LISTEN_IP, LISTEN_PORT))
sock.listen(1)

print('Modbus server listening on {}:{}'.format(LISTEN_IP, LISTEN_PORT))

# Accept incoming connections and start a new thread for each client
while True:
    client_sock, client_addr = sock.accept()
    print('Client connected from', client_addr)
    ModbusServerThread(client_sock).start()
