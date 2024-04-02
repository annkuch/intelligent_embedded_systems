from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accelerometer_file = accelerometer_filename
        self.gps_file = gps_filename
        self.parking_file = parking_filename
        self.data = {
            "accelerometer": [],
            "gps": [],
            "parking": []
        }
        self.index = {
            "accelerometer": 0,
            "gps": 0,
            "parking": 0
        }
        self.all_data_read = False

    def startReading(self):
        """Method to be called before reading data"""
        try:
            self.read_file(self.accelerometer_file, "accelerometer")
            self.read_file(self.gps_file, "gps")
            self.read_file(self.parking_file, "parking")
        except Exception as e:
            print(f"Error while attempting to open files: {e}")
            raise

    def read_file(self, filename: str, sensor_type: str):
        """Internal method to read data from a file"""
        with open(filename, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader) # Пропуск заголовку
            # Збереження решти рядків файлу у відповідний словник
            self.data[sensor_type] = list(csv_reader)

    def read(self) -> AggregatedData:
        """Method to return data from sensors"""
        # Повертає None, якщо всі дані вже прочитані
        if self.all_data_read:
            return None
        # Повертає None, якщо дані не були завантажені для всіх сенсорів
        if not all(self.data.values()):
            return None

        accelerometer_line = self.data["accelerometer"][self.index["accelerometer"]]
        gps_line = self.data["gps"][self.index["gps"]]
        parking_line = self.data["parking"][self.index["parking"]]

        accelerometer_data = list(map(float, accelerometer_line))
        gps_data = list(map(float, gps_line))
        parking_data = list(map(float, parking_line))

        # Оновлення поточних індексів кожного сенсора
        self.index["accelerometer"] = (self.index["accelerometer"] + 1) % len(self.data["accelerometer"])
        self.index["gps"] = (self.index["gps"] + 1) % len(self.data["gps"])
        self.index["parking"] = (self.index["parking"] + 1) % len(self.data["parking"])
        # Виклик методу stop_reading для перевірки завершення читання
        self.stopReading()

        return AggregatedData(
            Accelerometer(*accelerometer_data),
            Gps(*gps_data),
            Parking(parking_data[0], Gps(parking_data[1], parking_data[2])),
            datetime.now(),
            config.USER_ID,
        )

    def stopReading(self):
        """Method to be called to stop reading data"""
        # Перевірка, чи всі індекси дорівнюють 0, що означає завершення циклу читання
        if all(index == 0 for index in self.index.values()):
            self.all_data_read = True
