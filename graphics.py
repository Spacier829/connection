import time

import pyqtgraph as pg
from graphs.graph_gui import graph_gui
import serial
import serial.tools.list_ports

from connection import Connection

app = pg.mkQApp("GUI")
view = pg.GraphicsView()
layout = pg.GraphicsLayout()
view.setCentralItem(layout)
view.show()
# view.showMaximized()
view.setWindowTitle("Monitoring data from Block of Sensitive Sensors")

com_ports = pg.ComboBox()
ports = [port.device for port in serial.tools.list_ports.comports()]
com_ports.addItems(ports)
connect_btn = pg.QtWidgets.QPushButton("Подключиться")
connect_btn.setEnabled(False)
disconnect_btn = pg.QtWidgets.QPushButton("Отключиться")
disconnect_btn.setEnabled(False)
reconnect_btn = pg.QtWidgets.QPushButton("Переподключиться")
reconnect_btn.setEnabled(False)

timer = pg.QtCore.QTimer()

connection = Connection(com_ports.currentText())


def on_connect_clicked():
    connection.connect()
    time.sleep(5)
    connection.stop_event.set()
    connect_btn.setEnabled(False)
    disconnect_btn.setEnabled(True)
    reconnect_btn.setEnabled(True)
    timer.timeout.connect(update_graphics)
    timer.start(500)


def on_disconnect_clicked():
    connection.disconnect()
    connect_btn.setEnabled(True)
    disconnect_btn.setEnabled(False)
    reconnect_btn.setEnabled(False)
    timer.stop()


def on_reconnect_clicked():
    connection.reconnect()
    connect_btn.setEnabled(False)
    disconnect_btn.setEnabled(True)
    timer.timeout.connect(update_graphics)
    timer.start(500)


if com_ports.count() > 0:
    connect_btn.setEnabled(True)

connect_btn.clicked.connect(on_connect_clicked)

disconnect_btn.clicked.connect(on_disconnect_clicked)

reconnect_btn.clicked.connect(on_reconnect_clicked)

layout_ports = layout.addLayout()
com_ports_proxy = pg.QtWidgets.QGraphicsProxyWidget()
com_ports_proxy.setWidget(com_ports)
connect_proxy = pg.QtWidgets.QGraphicsProxyWidget()
connect_proxy.setWidget(connect_btn)
disconnect_proxy = pg.QtWidgets.QGraphicsProxyWidget()
disconnect_proxy.setWidget(disconnect_btn)
reconnect_proxy = pg.QtWidgets.QGraphicsProxyWidget()
reconnect_proxy.setWidget(reconnect_btn)
layout_ports.addItem(com_ports_proxy)
layout_ports.addItem(connect_proxy)
layout_ports.addItem(disconnect_proxy)
layout_ports.addItem(reconnect_proxy)

layout.nextRow()

angular_velocity_x = graph_gui()
angular_velocity_x.set_title("Угловая скорость X")
angular_velocity_y = graph_gui()
angular_velocity_y.set_title("Угловая скорость Y")
angular_velocity_z = graph_gui()
angular_velocity_z.set_title("Угловая скорость Z")

acceleration_x = graph_gui()
acceleration_x.set_title("Ускорение X")
acceleration_y = graph_gui()
acceleration_y.set_title("Ускорение Y")
acceleration_z = graph_gui()
acceleration_z.set_title("Ускорение Z")

temperature_FOG_x = graph_gui()
temperature_FOG_x.set_title("Температура ВОГ X")
temperature_FOG_y = graph_gui()
temperature_FOG_y.set_title("Температура ВОГ Y")
temperature_FOG_z = graph_gui()
temperature_FOG_z.set_title("Температура ВОГ Z")

temperature_AB_x = graph_gui()
temperature_AB_x.set_title("Температура БА X")
temperature_AB_y = graph_gui()
temperature_AB_y.set_title("Температура БА Y")
temperature_AB_z = graph_gui()
temperature_AB_z.set_title("Температура БА Z")

layout_angular_velocities = layout.addLayout(border=(100, 100, 100))
layout_angular_velocities.setContentsMargins(0, 0, 0, 0)
layout_angular_velocities.addItem(angular_velocity_x)
layout_angular_velocities.addItem(angular_velocity_y)
layout_angular_velocities.addItem(angular_velocity_z)

layout.nextRow()

layout_accelerations = layout.addLayout(border=(100, 100, 100))
layout_accelerations.setContentsMargins(0, 0, 0, 0)
layout_accelerations.addItem(acceleration_x)
layout_accelerations.addItem(acceleration_y)
layout_accelerations.addItem(acceleration_z)

layout.nextRow()

layout_temperatures_FOG = layout.addLayout(border=(100, 100, 100))
layout_temperatures_FOG.setContentsMargins(0, 0, 0, 0)
layout_temperatures_FOG.addItem(temperature_FOG_x)
layout_temperatures_FOG.addItem(temperature_FOG_y)
layout_temperatures_FOG.addItem(temperature_FOG_z)

layout.nextRow()

layout_temperatures_AB = layout.addLayout(border=(100, 100, 100))
layout_temperatures_AB.setContentsMargins(0, 0, 0, 0)
layout_temperatures_AB.addItem(temperature_AB_x)
layout_temperatures_AB.addItem(temperature_AB_y)
layout_temperatures_AB.addItem(temperature_AB_z)
layout.nextRow()


def update_graphics():
    values = connection.get_output_data()
    angular_velocity_x.update(values[1])
    angular_velocity_y.update(values[2])
    angular_velocity_z.update(values[3])
    acceleration_x.update(values[4])
    acceleration_y.update(values[5])
    acceleration_z.update(values[6])
    if values[7] == 0:
        temperature_FOG_x.update(values[8])
    elif values[7] == 1:
        temperature_FOG_y.update(values[8])
    elif values[7] == 2:
        temperature_FOG_z.update(values[8])
    elif values[7] == 3:
        temperature_AB_x.update(values[8])
    elif values[7] == 4:
        temperature_AB_y.update(values[8])
    elif values[7] == 5:
        temperature_AB_z.update(values[8])


if __name__ == '__main__':
    pg.exec()
