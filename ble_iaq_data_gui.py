# Ek olarak, 'pyqtgraph' kütüphanesini yüklemeyi unutmayın:
# pip install pyqtgraph

import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QLCDNumber, QWidget, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from bleak import BleakClient
import struct
import datetime
import pyqtgraph as pg

# Replace with your Arduino's BLE MAC address
DEVICE_MAC_ADDRESS = "F4:12:FA:9F:CE:59"

class BleakReader(QThread):
    data_ready = pyqtSignal(float, float, float, float, float)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def read_ble_data():
            async with BleakClient(DEVICE_MAC_ADDRESS) as client:
                while True:
                    services = client.services

                    temp = pressure = altitude = humidity = mq135 = 0
                    for service in services:
                        for characteristic in service.characteristics:
                            uuid = str(characteristic.uuid)
                            if uuid == "19b10002-e8f2-537e-4f6c-d104768a1214":  # Temperature UUID
                                temp_data = await client.read_gatt_char(uuid)
                                temp = struct.unpack('<f', temp_data)[0]
                            elif uuid == "19b10003-e8f2-537e-4f6c-d104768a1214":  # Pressure UUID
                                pressure_data = await client.read_gatt_char(uuid)
                                pressure = struct.unpack('<f', pressure_data)[0]
                            elif uuid == "19b10004-e8f2-537e-4f6c-d104768a1214":  # Altitude UUID
                                altitude_data = await client.read_gatt_char(uuid)
                                altitude = struct.unpack('<f', altitude_data)[0]
                            elif uuid == "19b10005-e8f2-537e-4f6c-d104768a1214":  # Humidity UUID
                                humidity_data = await client.read_gatt_char(uuid)
                                humidity = struct.unpack('<f', humidity_data)[0]
                            elif uuid == "19b10006-e8f2-537e-4f6c-d104768a1214":  # MQ135 UUID
                                mq135_data = await client.read_gatt_char(uuid)
                                mq135 = struct.unpack('<I', mq135_data)[0]

                    self.data_ready.emit(temp, pressure, altitude, humidity, mq135)

                    await asyncio.sleep(1)

        loop.run_until_complete(read_ble_data())

class AirQualityMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.start_time = datetime.datetime.now()  # Store the start time when the program begins

        # Set window title
        self.setWindowTitle("Air Quality Monitor")

        # Set window icon
        self.setWindowIcon(QIcon('images/air-quality-monitor.png'))

        # Initialize BLE Reader
        self.ble_reader = BleakReader()
        self.ble_reader.data_ready.connect(self.update_labels)
        self.ble_reader.start()

        # Setup UI
        self.setup_ui()

        # Read data at regular intervals using a timer
        self.timer = QTimer(self)
        self.timer.start(1000)  # Read data every 1000 milliseconds (1 second)

        # Update the clock every second
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def setup_ui(self):
        # Add QLCDNumber for clock
        self.lcd = QLCDNumber(self)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.setDigitCount(8)
        self.lcd.display(datetime.datetime.now().strftime("%H:%M:%S"))

        # Labels for sensor data
        self.sensor_label = QLabel("MQ135 Value: ")
        self.air_quality_label = QLabel("Air Quality: ")
        self.humidity_label = QLabel("Humidity: ")
        self.temperature_label = QLabel("Temperature: ")
        self.altitude_label = QLabel("Altitude: ")
        self.pressure_label = QLabel("Pressure: ")


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        layout.addWidget(self.sensor_label)
        layout.addWidget(self.air_quality_label)
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.altitude_label)
        layout.addWidget(self.pressure_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set font size
        font = QFont()
        font.setPointSize(11)
        self.sensor_label.setFont(font)
        self.air_quality_label.setFont(font)
        self.humidity_label.setFont(font)
        self.temperature_label.setFont(font)
        self.altitude_label.setFont(font)
        self.pressure_label.setFont(font)

        # Initialize graphs
        self.graphWidget_temp = pg.PlotWidget()
        self.graphWidget_temp.setBackground('w')
        self.graphWidget_temp.setTitle("Temperature Over Time")
        self.graphWidget_temp.setLabel('left', 'Temperature', units='°C')
        self.graphWidget_temp.setLabel('bottom', 'Time', units='')
        self.graphWidget_temp.showGrid(x=True, y=True)
        layout.addWidget(self.graphWidget_temp)

        self.graphWidget_humidity = pg.PlotWidget()
        self.graphWidget_humidity.setBackground('w')
        self.graphWidget_humidity.setTitle("Humidity Over Time")
        self.graphWidget_humidity.setLabel('left', 'Humidity', units='%')
        self.graphWidget_humidity.setLabel('bottom', 'Time', units='')
        self.graphWidget_humidity.showGrid(x=True, y=True)
        layout.addWidget(self.graphWidget_humidity)

        self.graphWidget_pressure = pg.PlotWidget()
        self.graphWidget_pressure.setBackground('w')
        self.graphWidget_pressure.setTitle("Pressure Over Time")
        self.graphWidget_pressure.setLabel('left', 'Pressure', units='hPa')
        self.graphWidget_pressure.setLabel('bottom', 'Time', units='')
        self.graphWidget_pressure.showGrid(x=True, y=True)
        layout.addWidget(self.graphWidget_pressure)

        self.graphWidget_altitude = pg.PlotWidget()
        self.graphWidget_altitude.setBackground('w')
        self.graphWidget_altitude.setTitle("Altitude Over Time")
        self.graphWidget_altitude.setLabel('left', 'Altitude', units='m')
        self.graphWidget_altitude.setLabel('bottom', 'Time', units='')
        self.graphWidget_altitude.showGrid(x=True, y=True)
        layout.addWidget(self.graphWidget_altitude)

        self.graphWidget_mq135 = pg.PlotWidget()
        self.graphWidget_mq135.setBackground('w')
        self.graphWidget_mq135.setTitle("MQ135 Values Over Time")
        self.graphWidget_mq135.setLabel('left', 'MQ135 Value', units='')
        self.graphWidget_mq135.setLabel('bottom', 'Time', units='')
        self.graphWidget_mq135.showGrid(x=True, y=True)
        layout.addWidget(self.graphWidget_mq135)

        # Set different pen colors for each graph
        self.pen_temp = pg.mkPen(color=(255, 0, 0), width=2)
        self.pen_humidity = pg.mkPen(color=(0, 0, 255), width=2)
        self.pen_pressure = pg.mkPen(color=(0, 255, 0), width=2)
        self.pen_altitude = pg.mkPen(color=(255, 0, 255), width=2)
        self.pen_mq135 = pg.mkPen(color=(255, 165, 0), width=2)

        self.graph_data_x_temp = []
        self.graph_data_y_temp = []

        self.graph_data_x_humidity = []
        self.graph_data_y_humidity = []

        self.graph_data_x_pressure = []
        self.graph_data_y_pressure = []

        self.graph_data_x_altitude = []
        self.graph_data_y_altitude = []

        self.graph_data_x_mq135 = []
        self.graph_data_y_mq135 = []

    def update_labels(self, temp, pressure, altitude, humidity, mq135):
        self.temperature_label.setText(f"Temperature: {temp:.2f} °C")
        self.air_quality_label.setText("Air Quality: Good" if mq135 < 200 else "Air Quality: Moderate"
                                        if 200 <= mq135 < 400 else "Air Quality: Poor")
        self.humidity_label.setText(f"Humidity: {humidity:.2f} %")
        self.sensor_label.setText(f"MQ135 Value: {mq135}")
        self.altitude_label.setText(f"Altitude: {altitude:.2f} meters")
        self.pressure_label.setText(f"Pressure: {pressure:.3f} hPa")

        timestamp = datetime.datetime.now()
        elapsed_time = timestamp - self.start_time  # Calculate elapsed time from the start
        elapsed_seconds = elapsed_time.total_seconds()  # Convert elapsed time to seconds

        # Append elapsed time to x-axis data
        self.graph_data_x_temp.append(elapsed_seconds)
        self.graph_data_y_temp.append(temp)
        self.graph_data_x_humidity.append(elapsed_seconds)
        self.graph_data_y_humidity.append(humidity)
        self.graph_data_x_pressure.append(elapsed_seconds)
        self.graph_data_y_pressure.append(pressure)
        self.graph_data_x_altitude.append(elapsed_seconds)
        self.graph_data_y_altitude.append(altitude)
        self.graph_data_x_mq135.append(elapsed_seconds)
        self.graph_data_y_mq135.append(mq135)

        # Plot data for each sensor
        self.graphWidget_temp.plot(self.graph_data_x_temp, self.graph_data_y_temp, pen=self.pen_temp, clear=True)
        self.graphWidget_humidity.plot(self.graph_data_x_humidity, self.graph_data_y_humidity, pen=self.pen_humidity, clear=True)
        self.graphWidget_pressure.plot(self.graph_data_x_pressure, self.graph_data_y_pressure, pen=self.pen_pressure, clear=True)
        self.graphWidget_altitude.plot(self.graph_data_x_altitude, self.graph_data_y_altitude, pen=self.pen_altitude, clear=True)
        self.graphWidget_mq135.plot(self.graph_data_x_mq135, self.graph_data_y_mq135, pen=self.pen_mq135, clear=True)

    def update_clock(self):
        # Update the clock display
        self.lcd.display(datetime.datetime.now().strftime("%H:%M:%S"))

def main():
    app = QApplication(sys.argv)
    window = AirQualityMonitor()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
