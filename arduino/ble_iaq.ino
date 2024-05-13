#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ArduinoBLE.h>

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define SERVICE_UUID "19B10000-E8F2-537E-4F6C-D104768A1214" // BLE service UUID
#define TEMPERATURE_UUID "19B10002-E8F2-537E-4F6C-D104768A1214"
#define PRESSURE_UUID "19B10003-E8F2-537E-4F6C-D104768A1214"
#define ALTITUDE_UUID "19B10004-E8F2-537E-4F6C-D104768A1214"
#define HUMIDITY_UUID "19B10005-E8F2-537E-4F6C-D104768A1214"
#define MQ135_UUID "19B10006-E8F2-537E-4F6C-D104768A1214"

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme;
BLEService sensorService(SERVICE_UUID); // Create BLE service
BLEFloatCharacteristic temperatureCharacteristic(TEMPERATURE_UUID, BLERead | BLENotify);
BLEFloatCharacteristic pressureCharacteristic(PRESSURE_UUID, BLERead | BLENotify);
BLEFloatCharacteristic altitudeCharacteristic(ALTITUDE_UUID, BLERead | BLENotify);
BLEFloatCharacteristic humidityCharacteristic(HUMIDITY_UUID, BLERead | BLENotify);
BLEUnsignedIntCharacteristic mq135Characteristic(MQ135_UUID, BLERead | BLENotify);

#define BUZZER_PIN 8 // Digital pin connected to the buzzer

unsigned long previousMillis = 0;
const long interval = 1000;

void setup() {
  Serial.begin(9600); // Start serial communication, set baud rate
  pinMode(BUZZER_PIN, OUTPUT); // Set the buzzer pin as output
  while (!Serial); // Wait for serial connection
  if (!bme.begin(0x76)) {
    Serial.println("Could not find BME280 sensor, check wiring!");
    while (1);
  }

  BLE.begin(); // Start BLE communication

  // Add characteristics to BLE service
  sensorService.addCharacteristic(temperatureCharacteristic);
  sensorService.addCharacteristic(pressureCharacteristic);
  sensorService.addCharacteristic(altitudeCharacteristic);
  sensorService.addCharacteristic(humidityCharacteristic);
  sensorService.addCharacteristic(mq135Characteristic);

  // Add service to advertisement data
  BLE.setAdvertisedService(sensorService);
  // Start the service
  BLE.addService(sensorService);

  // Subscribe to characteristics
  temperatureCharacteristic.setValue(0);
  pressureCharacteristic.setValue(0);
  altitudeCharacteristic.setValue(0);
  humidityCharacteristic.setValue(0);
  mq135Characteristic.setValue(0);
  BLE.setLocalName("BME280 Sensor");
  BLE.advertise();

  Serial.println("BLE Central device initialized, don't worry!");
}

void loop() {
  // Listen for BLE requests
  BLEDevice central = BLE.central();

  // Check if a BLE central device is connected
  if (central) {
    Serial.print("Connected device: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Read sensor data
      int mq135 = analogRead(A0);
      float bme280_temp = bme.readTemperature();
      float bme280_pressure = bme.readPressure() / 100.0F;
      float bme280_altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
      float bme280_humidity = bme.readHumidity();

      // Send data over BLE
      mq135Characteristic.writeValue(mq135);
      temperatureCharacteristic.writeValue(bme280_temp);
      pressureCharacteristic.writeValue(bme280_pressure);
      altitudeCharacteristic.writeValue(bme280_altitude);
      humidityCharacteristic.writeValue(bme280_humidity);

      // Check limits and control the buzzer
      checkLimitsAndBuzzer(bme280_temp, bme280_pressure, bme280_altitude, bme280_humidity, mq135);

      // Wait for the interval
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        Serial.println("Sending data over BLE...");
      }
    }
  }
}

void checkLimitsAndBuzzer(float temp, float pressure, float altitude, float humidity, int mq135) {
  // Define your limits here
  float temp_upper_limit = 30.0;
  float temp_lower_limit = 20.0;
  float pressure_upper_limit = 1100.0;
  float pressure_lower_limit = 900.0;
  int mq135_upper_limit = 200;
  int mq135_lower_limit = 0;

  // Check temperature limits
  if (temp > temp_upper_limit || temp < temp_lower_limit) {
    tone(BUZZER_PIN, 1000, 500); // Play a high-pitched tone
  }

  // Check pressure limits
  if (pressure > pressure_upper_limit || pressure < pressure_lower_limit) {
    tone(BUZZER_PIN, 1500, 500); // Play a medium-pitched tone
  }

  // Check MQ135 limits
  if (mq135 > mq135_upper_limit || mq135 < mq135_lower_limit) {
    tone(BUZZER_PIN, 2000, 500); // Play a low-pitched tone
  }
}
