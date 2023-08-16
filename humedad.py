from machine import Pin, ADC
import network
import time
import urequests

# Conexión a la red Wi-Fi
ssid = "W-Administrativos"
password = "W1$21!pst@r"
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
while not station.isconnected():
    pass
print("Conexión a la red Wi-Fi establecida")

# Configuración del sensor de humedad
soil = ADC(Pin(35))
min_moisture = 0
max_moisture = 4095

soil.atten(ADC.ATTN_11DB)       # Full range: 3.3v
soil.width(ADC.WIDTH_12BIT)     # Range 0 to 4095

# Define the pump pin
pump_pin = Pin(2, Pin.OUT)  # Use the appropriate pin number for your pump setup

# Función para calcular la humedad del suelo
def calculate_moisture(soil_value):
    m = (max_moisture - soil_value) * 100 / (max_moisture - min_moisture)
    return m

# Función para enviar humedad actualizada a la API Flask
def update_humidity_in_api(humidity):
    server_url = "http://10.2.2.193:5000/api/plantitas/update_humidity"  # Reemplaza con tu dirección IP
    data = {
        "humedad": humidity,
    }
    try:
        response = urequests.patch(server_url, json=data)
        response.close()
        return response.status_code
    except Exception as e:
        print('Error al actualizar la humedad:', e)
        return None

# Función para obtener la humedad almacenada en la base de datos desde diferentes rutas
def get_humidity_from_api(url):
    try:
        response = urequests.get(url)
        data = response.json()
        response.close()

        # Verificar si la respuesta es una lista de diccionarios
        if isinstance(data, list):
            first_item = data[0]
            return first_item.get("humedad", None)
        else:
            return data.get("humedad", None)
    except Exception as e:
        print('Error al obtener la humedad desde la API:', e)
        return None


print("Leyendo valores de humedad del suelo y enviando datos...")
while True:
    try:
        soil_value = soil.read()
        moisture = calculate_moisture(soil_value)
        print('Humedad del suelo:', moisture, '%')
        
        status_code = update_humidity_in_api(moisture)
        if status_code is not None:
            if status_code == 200:
                print('Humedad actualizada correctamente en la API Flask.')
            else:
                print('Error al actualizar la humedad. Código de estado:', status_code)
        
        # Obtener la humedad almacenada desde la segunda ruta
        stored_humidity2 = get_humidity_from_api("http://10.2.2.193:5000/api/plantita")
        
        if stored_humidity2 is not None:
            print('Humedad almacenada en la base de datos 2:', stored_humidity2, '%')
            
            if stored_humidity2 < 30:
                pump_pin.off()  # Turn on the pump when stored humidity is less than 30
                print('Encendiendo la bomba de agua.')
            else:
                pump_pin.on()  # Turn off the pump when stored humidity is not less than 30
                print('Apagando la bomba de agua.')

        time.sleep(10)
    except Exception as e:
        print('Error en el bucle principal:', e)

