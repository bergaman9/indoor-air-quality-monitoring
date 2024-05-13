# Indoor Air Quality Monitoring and Warning System

![System Demo](demo.gif)

## Description
The Indoor Air Quality Monitoring and Warning System is a project developed for monitoring and analyzing indoor air quality in real-time. It utilizes Arduino Uno R4 WiFi microcontroller along with various sensors to collect data on temperature, humidity, pressure, air quality, and more. The collected data is processed using Python and displayed in real-time using PyQt5 for desktop visualization. The system is designed to work offline without the need for external databases or web interfaces, making it suitable for standalone usage.

## Features
- Real-time monitoring of indoor air quality
- Wireless data transmission via Bluetooth Low Energy
- Data processing and visualization using PyQt5 and Python libraries
- User-friendly desktop interface for real-time visualization
- Historical data tracking and trend analysis
- No external database or web interface dependencies

## Installation
1. Clone the repository: `git clone https://github.com/username/repository.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Connect the Arduino Uno R4 WiFi and sensors
4. Run the main script: `python ble_iaq_data_gui.py`

## Usage
- Access the desktop interface by running the GUI application.
- Monitor real-time air quality metrics and receive alerts when thresholds are exceeded.
- Analyze historical data using visualization tools provided in the desktop interface.

## Future Enhancements
- Integration of additional sensors for comprehensive monitoring
- Development of predictive models for proactive alerts
- Enhancement of hardware setup and user interfaces

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
