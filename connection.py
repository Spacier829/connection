import threading
import time
import serial
import serial.tools.list_ports
from queue import Queue
from threading import Thread, Lock
from loguru import logger
import numpy


class Connection:
    COUNTER_ALL_FRAMES = 0
    COUNTER_GOOD_FRAMES = 0
    COUNTER_BAD_FRAMES = 0  # counter of frames with not valid CRC

    port_name = ''
    baudrate = 115200
    device = serial.Serial()
    ports = serial.tools.list_ports.comports()

    lock = Lock()
    stop_event = threading.Event()

    output_data = Queue()

    logger.add(time.strftime("logs/" + '%d-%m-%Y_%H-%M') + ".log",
               format="{time:MMMM DD, YYYY > HH:mm:ss} |"
                      " {level: <8} | {name}:{function}:{line} | {message} ")

    # rotation="10 MB", compression="zip", )

    def __init__(self):
        for port in sorted(self.ports):
            print(port.serial_number)
        # self.port_name = input("Write serial port name (ex: COM1): ")
        self.port_name = "COM4"

    def connect(self):
        try:
            self.stop_event.clear()
            self.device = serial.Serial(self.port_name, self.baudrate)
            connection_thread = Thread(target=self.read_packet,
                                       args=(self.stop_event,))
            connection_thread.start()
        except serial.serialutil.SerialException:
            logger.warning("Can't connect to: " + self.port_name)

    def disconnect(self):
        if self.device.is_open:
            self.stop_event.set()
            self.device.close()
            logger.info(self.port_name + " is disconnected")
        else:
            logger.info(self.port_name + " is already disconnected")

    def reconnect(self):
        self.disconnect()
        self.connect()

    def read_packet(self, stop_event):
        header = b'\xc0\xc0'
        packets_buff = b''
        err_cnt = 0
        while not stop_event.is_set():
            time.sleep(0.005)
            packet = self.device.read_all()
            if packet == b'':
                logger.warning(self.port_name + " can't get data")
                self.stop_event.set()
            else:
                packets_buff += packet
            while len(packets_buff) >= 32:
                if packets_buff.startswith(header):
                    if self.is_crc_valid(packets_buff[:32]):
                        data_frame = packets_buff[:32]
                        self.get_frame_info(data_frame)
                        packets_buff = packets_buff[32:]
                    else:
                        logger.critical(packets_buff[:32])
                        packets_buff = packets_buff[1:]
                        self.COUNTER_ALL_FRAMES += 1
                        self.COUNTER_BAD_FRAMES += 1
                        err_cnt += 1
                else:
                    logger.critical(packets_buff)
                    packets_buff = packets_buff[1:]
                    err_cnt += 1
                    logger.warning(err_cnt)

    def is_crc_valid(self, data_frame):
        read_crc = hex(int.from_bytes(bytearray(data_frame[30:]), "little"))
        calculated_crc = self.crc_16(data_frame)

        if calculated_crc == read_crc:
            return True
        else:
            return False

    def crc_16(self, data_frame):
        polynomial = 0x1021
        data = data_frame[2:30]
        crc = 0xFFFF

        for c in data:
            crc ^= (c << 8)
            for j in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc = crc << 1

        crc = crc & 0xFFFF
        crc = hex(crc)
        return crc

    def get_frame_info(self, data_frame):
        self.COUNTER_ALL_FRAMES += 1
        self.COUNTER_GOOD_FRAMES += 1
        log_info = ("ALL: ", self.COUNTER_ALL_FRAMES, ", GOOD: ",
                    self.COUNTER_GOOD_FRAMES,
                    ", BAD: ", self.COUNTER_BAD_FRAMES)
        logger.info(log_info)

        result_data_frame_values = numpy.zeros(9)

        # Данные в массиве result_data_frame_values имеют следующую структуру:
        # 0 - порядковый номер фрейма, берется на основе считанных фреймов
        #     с правильной CRC
        # 1 - Угловая скорость X (Gx)
        # 2 - Угловая скорость Y (Gy)
        # 3 - Угловая скорость Z (Gz)
        # 4 - Ускорение X (Ax)
        # 5 - Ускорение Y (Ay)
        # 6 - Ускорение Z (Az)
        # 8 - Номер температурного датчика
        # 9 - Значение температуры телеметрии (ADD)

        result_data_frame_values[0] = self.COUNTER_GOOD_FRAMES
        result_data_frame_values[1], result_data_frame_values[2], \
            result_data_frame_values[3] = self.calculate_angular_velocity(
            data_frame)
        result_data_frame_values[4], result_data_frame_values[5], \
            result_data_frame_values[6] = self.calculate_acceleration(
            data_frame)
        result_data_frame_values[7], result_data_frame_values[
            8] = self.calculate_telemetry(data_frame)

        with self.lock:
            self.output_data.put(result_data_frame_values)

    def calculate_angular_velocity(self, data_frame):
        angular_velocity_x_value = int.from_bytes(bytearray(data_frame[2:6]),
                                                  "little") * (
                                           1.085069 * (10 ** (-6)))
        angular_velocity_y_value = int.from_bytes(bytearray(data_frame[6:10]),
                                                  "little") * (
                                           1.085069 * (10 ** (-6)))
        angular_velocity_z_value = int.from_bytes(bytearray(data_frame[10:14]),
                                                  "little") * (
                                           1.085069 * (10 ** (-6)))

        return (angular_velocity_x_value, angular_velocity_y_value,
                angular_velocity_z_value)

    def calculate_acceleration(self, data_frame):
        acceleration_x_value = int.from_bytes(bytearray(data_frame[14:18]),
                                              "little") * 1.0 * (10 ** (-4))
        acceleration_y_value = int.from_bytes(bytearray(data_frame[18:22]),
                                              "little") * 1.0 * (10 ** (-4))
        acceleration_z_value = int.from_bytes(bytearray(data_frame[22:26]),
                                              "little") * 1.0 * (10 ** (-4))

        return acceleration_x_value, acceleration_y_value, acceleration_z_value

    def calculate_telemetry(self, data_frame):
        counter_frames = bin(int.from_bytes((data_frame[28].to_bytes()),
                                            "little"))
        bit_data = int(counter_frames, 2)
        temperature_value = int.from_bytes(bytearray(data_frame[26:28]),
                                           "little") * 0.01

        return bit_data, temperature_value

    def get_output_data(self):
        if not self.output_data.empty():
            with self.lock:
                return self.output_data.get()
        else:
            logger.warning("Output data is empty")


if __name__ == "__main__":
    connection = Connection()
    connection.connect()
    # while True:
    #     time.sleep(0.5)
    #     a = connection.get_output_data()
    #     logger.info(a)
