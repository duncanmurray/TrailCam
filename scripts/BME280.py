import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
bme280data = bme280.sample(bus, address, calibration_params)

# the compensated_reading class has the following attributes
print(bme280data.id)
print(bme280data.timestamp)
print(bme280data.temperature)
print(bme280data.pressure)
print(bme280data.humidity)

# there is a handy string representation too
print(bme280data)

temp = round(bme280data.temperature,1)
print(temp)
