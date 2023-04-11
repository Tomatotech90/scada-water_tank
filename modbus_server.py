from pyModbusTCP.server import ModbusServer

server = ModbusServer(host="localhost", port=502)

def add_water(tank_id):
    # Add water to the specified tank
    pass

def discharge_water(tank_id):
    # Discharge water from the specified tank
    pass

def update_percentage(tank_id, percentage):
    # Update the water level of the specified tank
    pass

def add_to_log(message, type):
    # Add the message to the log
    pass

def read_registers_callback(request):
    # Callback function to handle incoming read register requests
    # Return the water level of the specified tank
    pass

def write_registers_callback(request):
    # Callback function to handle incoming write register requests
    # Update the water level of the specified tank
    pass

server.start()
server.add_read_callback(slave_id=1, function_code=3, callback=read_registers_callback)
server.add_write_callback(slave_id=1, function_code=6, callback=write_registers_callback)
