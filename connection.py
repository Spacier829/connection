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
    # Counter of frames with not valid CRC
    COUNTER_BAD_FRAMES = 0
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
        self.port_name = "COM2"

    def device_is_connected(self):
        return self.device.is_open

    def connect(self):
        try:
            self.device = serial.Serial(self.port_name, self.baudrate)
            connection_thread = Thread(target=self.read_data,
                                       args=(self.stop_event,))
            connection_thread.start()
        except serial.serialutil.SerialException:
            logger.warning("Can't connect to: ", self.port_name)

    def disconnect(self):
        if self.device_is_connected():
            self.device.close()
            self.stop_event.set()
        else:
            logger.info(self.port_name, " is already disconnected")

    def reconnect(self):
        self.disconnect()
        self.connect()
        # time.sleep(0.1)
        # read_data = self.device.read_all()
        # if read_data == b'':

    def read_data(self):
        header = b'\xc0\xc0'
        data_frame = 0
        # test = b'\xaf\xdb\xff\xff>\x8c\x00\x00:#\xfe\xff\xa3\x7f\x01\x00.\xf5\xff\xff\xc7\xfe\xff\xff\x9a\x08\xfa&S\x12\xc0\xc0?\xcc\xff\xff\xb6\xfe\x00\x00\x18\xcb\xfc\xff\x1c\x80\x01\x00X\xf5\xff\xff\x1c\xff\xff\xff\xc0\t\xfb&J8\xc0\xc0\x14\xd3\xff\xff\xe72\x01\x00\xb4j\xfc\xff\x93\x7f\x01\x00\x90\xf5\xff\xff\xec\xfe\xff\xff\xc0\t\xfc&\xe0\x89\xc0\xc0\xa4\xd0\xff\xff\x86\x9d\x01\x00\x1e\xc4\xfb\xff\xa9\x7f\x01\x00\xa9\xf5\xff\xff\xbf\xfe\xff\xff\xc0\t\xfd&DJ\xc0\xc0Z\xce\xff\xff}\xdf\x01\x00\x11\x0b\xfc\xffy\x7f\x01\x00\xd0\xf5\xff\xff\xe0\xfe\xff\xff\x9a\x08\xfe&\xf6#\xc0\xc0\x9f\xd8\xff\xffM0\x02\x00R\xc2\xfb\xffA\x7f\x01\x00I\xf6\xff\xff%\xff\xff\xff\xc0\t\xff&\xcdr\xc0\xc01\xe2\xff\xffZ\xfa\x01\x00\xc1V\xfc\xff\x95~\x01\x00C\xf6\xff\xff\x18\xff\xff\xff\x9a\x08\x00\'\xf0w\xc0\xc0\xbe\xe9\xff\xff\xd6\xd5\x01\x00GM\xfc\xffZ~\x01\x00\x05\xf6\xff\xff\x12\xff\xff\xff\x9a\x08\x01\'\x1e\xd9\xc0\xc0\xc4\xe8\xff\xff9l\x01\x00\xf7\x01\xfd\xff^~\x01\x00\xdf\xf5\xff\xff\x80\xfe\xff\xff\x9a\x08\x02\'\xf4\xa7\xc0\xc0\xbb\xe4\xff\xff\xf9\x1e\x01\x00\xa2\xf6\xfc\xff\xed~\x01\x00=\xf5\xff\xff\xe5\xfe\xff\xff\xc0\t\x03\'\xd6O\xc0\xc0 \xed\xff\xff\x06\x9d\x00\x00*\x84\xfd\xff#\x7f\x01\x00\xe5\xf5\xff\xff\xc2\xfe\xff\xff\xc0\t\x04\'p\xa9\xc0\xc0g\xeb\xff\xff\xf9\x86\x00\x00Ac\xfd\xff\xfc~\x01\x00\xaa\xf5\xff\xff\x92\xfe\xff\xff\xc0\t\x05\'?\x03\xc0\xc0^\xec\xff\xff\x9fi\x00\x00\t\x14\xfe\xffT\x7f\x01\x00\xa6\xf5\xff\xff{\xfe\xff\xff\x9a\x08\x06\'\xd8\xfa\xc0\xc0\xf5\xef\xff\xff\x9f~\x00\x00\xb2Y\xfe\xffg\x7f\x01\x00\xab\xf5\xff\xff\x08\xfe\xff\xff\xc0\t\x07\'\xc4\'\xc0\xc0\xb4\xfd\xff\xffWV\x00\x00\x0f\\\xff\xffb\x7f\x01\x00\x1a\xf6\xff\xffe\xfe\xff\xff\x9a\x08\x08\'>\x96\xc0\xc0:\xfd\xff\xff\x05~\x00\x00K\x89\xff\xff\x8d\x7f\x01\x00\x90\xf5\xff\xff\xbc\xfd\xff\xff\x9a\x08\t\'\x0b(\xc0\xc0\xbb\xfa\xff\xff#v\x00\x00\xddO\x00\x00\x1b\x7f\x01\x00D\xf5\xff\xffj\xfd\xff\xff\x9a\x08\n\'\x85?\xc0\xc0\xf6\xee\xff\xff!\x95\x00\x00\x943\x00\x00\xe9~\x01\x00\xc7\xf5\xff\xffT\xfd\xff\xff\xc0\t\x0b\'\xeb\xf4\xc0\xc0\xc9\xf5\xff\xff\xc3O\x00\x008\x8f\x00\x00\xdb~\x01\x00\xfe\xf5\xff\xffy\xfd\xff\xff\xc0\t\x0c\'\xb8&\xc0\xc0l\x01\x00\x00"2\x00\x00*$\x00\x00\xfb~\x01\x00p\xf5\xff\xffP\xfd\xff\xff\xc0\t\r\'\x17\x9f\xc0\xc0\xac\x07\x00\x00I\xe9\xff\xff\x9ar\x00\x00\x9d~\x01\x00O\xf5\xff\xff\x80\xfd\xff\xff\x9a\x08\x0e\'\xe6\xcd\xc0\xc0n\x00\x00\x00K\xe0\xff\xff\xe3\x01\x00\x00\x0c\x7f\x01\x00\xfd\xf4\xff\xff\xeb\xfc\xff\xff\xc0\t\x0f\'\'\xa0\xc0\xc0\xa1\t\x00\x00\xa3\xc5\xff\xff\xcf\x0f\x00\x00\x99\x7f\x01\x00\xfb\xf4\xff\xff)\xfd\xff\xff\x9a\x08\x10\'\xa1G\xc0\xc0\xad\x04\x00\x00\xfd\xb6\xff\xff\x14\x95\xff\xff\xf2~\x01\x00k\xf4\xff\xff\xf9\xfc\xff\xff\x9a\x08\x11\'\x17F\xc0\xc0%\xff\xff\xff\xbb\xa7\xff\xff\x8b\x13\x00\x00S\x7f\x01\x00s\xf4\xff\xff\xdb\xfc\xff\xff\x9a\x08\x12\'5K\xc0\xc0F\xf9\xff\xff\x04\xe6\xff\xff\xf2\t\x00\x00Z\x7f\x01\x00N\xf5\xff\xff\xa2\xfc\xff\xff\xc0\t\x13\'W\r\xc0\xc0\xdb\xf6\xff\xff\x94\xc2\xff\xff\xfb\xbe\x00\x009\x7f\x01\x00\x9d\xf5\xff\xff\xd7\xfc\xff\xff\xc0\t\x14\'H\xaf\xc0\xc07\xf5\xff\xff\x8c\xd0\xff\xff\x0b\xc2\x00\x00R\x7f\x01\x001\xf5\xff\xff\xe3\xfc\xff\xff\xc0\t\x15\'\xbf\x82\xc0\xc0I\xfa\xff\xff\xcf\xc4\xff\xff\x86Z\x01\x00V\x7f\x01\x00-\xf5\xff\xff$\xfd\xff\xff\x9a\x08\x16\'\xfb\x03\xc0\xc0\xf7\xfe\xff\xff\x8f\xf2\xff\xff\x80\xf3\x00\x00$\x7f\x01\x00\xaa\xf5\xff\xff\xa7\xfd\xff\xff\xc0\t\x17\'\x1a\xa3\xc0\xc0\xfd\x05\x00\x00\x0c\xda\xff\xff\xf1\xe9\x00\x00\x1e\x7f\x01\x00\xc2\xf5\xff\xff\xfe\xfc\xff\xff\x9a\x08\x18\'\xbc\x1d\xc0\xc0$\x02\x00\x00*\xe3\xff\xff\r7\x00\x00\x19\x7f\x01\x00\x85\xf5\xff\xff7\xfd\xff\xff\x9a\x08\x19\'\x91\xaf\xc0\xc0c\x00\x00\x00\x81\xc5\xff\xff\x93\t\x00\x00\x05\x7f\x01\x00f\xf5\xff\xff\xb7\xfd\xff\xff\x9a\x08\x1a\'\x1c\x90\xc0\xc0\xc5\xf0\xff\xff\xb1\x03\x00\x00\xe0B\xff\xffF\x7f\x01\x00\xab\xf4\xff\xffX\xfd\xff\xff\xc0\t\x1b\'\xe0\x15\xc0\xc0\x1e\xf2\xff\xff6\xf4\xff\xff\xce:\xff\xff\xb0\x7f\x01\x00\x10\xf5\xff\xff\x92\xfd\xff\xff\xc0\t\x1c\'\x9c\x12\xc0\xc0\xad\xee\xff\xffm\x0f\x00\x004\xe4\xfe\xff/\x7f\x01\x00\x95\xf5\xff\xff\xb7\xfd\xff\xff\xc0\t\x1d\'*#\xc0\xc0e\xf5\xff\xff\xd3\xfd\xff\xffSy\xff\xffO\x7f\x01\x00d\xf5\xff\xff\xcc\xfd\xff\xff\x9a\x08\x1e\'\x06\xef'
        while self.device_is_connected():
            time.sleep(0.01)
            read_packet = self.device.read_all()
            if read_packet == b'':
                self.reconnect()
            # read_packet = test
            while read_packet != 0:
                start_header = read_packet.find(header)
                if start_header != -1:
                    if data_frame == 0:
                        end_header = start_header + 32
                        if end_header <= len(read_packet):
                            data_frame = read_packet[
                                         start_header:end_header]
                            if self.is_crc_valid(data_frame):
                                self.get_frame_info(data_frame)
                                data_frame = 0
                                read_packet = read_packet[end_header:]
                            else:
                                start_header += 1
                                end_header += 1
                                if end_header <= len(read_packet):
                                    data_frame = read_packet[
                                                 start_header:end_header]
                                    if self.is_crc_valid(data_frame):
                                        self.get_frame_info(data_frame)
                                        data_frame = 0
                                        read_packet = read_packet[end_header:]
                                    else:
                                        self.COUNTER_ALL_FRAMES += 1
                                        self.COUNTER_BAD_FRAMES += 1
                                        logger.critical(data_frame)
                                        data_frame = 0
                                        read_packet = read_packet[end_header:]
                                else:
                                    data_frame = read_packet[start_header:]
                                    read_packet = 0
                        else:
                            data_frame = read_packet[start_header:]
                            read_packet = 0
                    else:
                        end_header = start_header
                        if data_frame == b'\xc0' and start_header == 0:
                            end_header = end_header + 31
                        if len(data_frame) + end_header < 32:
                            end_header += 1
                        data_frame = data_frame + read_packet[:end_header]
                        if self.is_crc_valid(data_frame):
                            self.get_frame_info(data_frame)
                            data_frame = 0
                            read_packet = read_packet[end_header:]
                        else:
                            end_header += 1
                            if end_header <= len(read_packet):
                                logger.info(data_frame)
                                data_frame = data_frame[1:] + read_packet[
                                    end_header].to_bytes()
                                logger.info(data_frame)
                                if self.is_crc_valid(data_frame):
                                    self.get_frame_info(data_frame)
                                    data_frame = 0
                                    read_packet = read_packet[end_header:]
                                else:
                                    self.COUNTER_ALL_FRAMES += 1
                                    self.COUNTER_BAD_FRAMES += 1
                                    logger.critical(data_frame)
                                    data_frame = 0
                                    read_packet = read_packet[end_header:]
                            else:
                                read_packet = 0
                elif data_frame != 0:
                    data_frame = data_frame + read_packet
                    read_packet = 0
                elif read_packet == b'\xc0':
                    data_frame = read_packet
                    read_packet = 0
                else:
                    read_packet = 0

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
                logger.info(self.output_data.qsize())
                return self.output_data.get()
        else:
            time.sleep(.5)
            logger.warning("Output data is empty")


connection = Connection()
connection.connect()

# while True:
#     a = connection.get_output_data()
#     logger.info(a)
