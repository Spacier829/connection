import pyqtgraph as pg
from graphs.graph_gui import graph_gui
import serial.tools.list_ports

from connection import Connection


class MonitoringApp(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.com_ports = pg.ComboBox()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_ports.addItems(ports)
        self.connect_btn = pg.QtWidgets.QPushButton("Подключиться")
        self.connect_btn.setEnabled(False)
        self.disconnect_btn = pg.QtWidgets.QPushButton("Отключиться")
        self.disconnect_btn.setEnabled(False)
        self.reconnect_btn = pg.QtWidgets.QPushButton("Переподключиться")
        self.reconnect_btn.setEnabled(False)

        self.com_ports.textActivated.connect(self.com_ports_changed)

        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.disconnect_btn.clicked.connect(self.on_disconnect_clicked)
        self.reconnect_btn.clicked.connect(self.on_reconnect_clicked)

        self.timer = pg.QtCore.QTimer()
        self.connection = Connection(self.com_ports.currentText())

        layout = pg.GraphicsLayout()
        layout_ports = layout.addLayout()
        com_ports_proxy = pg.QtWidgets.QGraphicsProxyWidget()
        com_ports_proxy.setWidget(self.com_ports)
        connect_proxy = pg.QtWidgets.QGraphicsProxyWidget()
        connect_proxy.setWidget(self.connect_btn)
        disconnect_proxy = pg.QtWidgets.QGraphicsProxyWidget()
        disconnect_proxy.setWidget(self.disconnect_btn)
        reconnect_proxy = pg.QtWidgets.QGraphicsProxyWidget()
        reconnect_proxy.setWidget(self.reconnect_btn)
        layout_ports.addItem(com_ports_proxy)
        layout_ports.addItem(connect_proxy)
        layout_ports.addItem(disconnect_proxy)
        layout_ports.addItem(reconnect_proxy)

        layout.nextRow()

        self.angular_velocity_x = graph_gui()
        self.angular_velocity_x.set_title("Угловая скорость X")
        self.angular_velocity_y = graph_gui()
        self.angular_velocity_y.set_title("Угловая скорость Y")
        self.angular_velocity_z = graph_gui()
        self.angular_velocity_z.set_title("Угловая скорость Z")

        self.acceleration_x = graph_gui()
        self.acceleration_x.set_title("Ускорение X")
        self.acceleration_y = graph_gui()
        self.acceleration_y.set_title("Ускорение Y")
        self.acceleration_z = graph_gui()
        self.acceleration_z.set_title("Ускорение Z")

        self.temperature_FOG_x = graph_gui()
        self.temperature_FOG_x.set_title("Температура ВОГ X")
        self.temperature_FOG_y = graph_gui()
        self.temperature_FOG_y.set_title("Температура ВОГ Y")
        self.temperature_FOG_z = graph_gui()
        self.temperature_FOG_z.set_title("Температура ВОГ Z")

        self.temperature_AB_x = graph_gui()
        self.temperature_AB_x.set_title("Температура БА X")
        self.temperature_AB_y = graph_gui()
        self.temperature_AB_y.set_title("Температура БА Y")
        self.temperature_AB_z = graph_gui()
        self.temperature_AB_z.set_title("Температура БА Z")

        layout_angular_velocities = layout.addLayout(border=(100, 100, 100))
        layout_angular_velocities.setContentsMargins(0, 0, 0, 0)
        layout_angular_velocities.addItem(self.angular_velocity_x)
        layout_angular_velocities.addItem(self.angular_velocity_y)
        layout_angular_velocities.addItem(self.angular_velocity_z)

        layout.nextRow()

        layout_accelerations = layout.addLayout(border=(100, 100, 100))
        layout_accelerations.setContentsMargins(0, 0, 0, 0)
        layout_accelerations.addItem(self.acceleration_x)
        layout_accelerations.addItem(self.acceleration_y)
        layout_accelerations.addItem(self.acceleration_z)

        layout.nextRow()

        layout_temperatures_FOG = layout.addLayout(border=(100, 100, 100))
        layout_temperatures_FOG.setContentsMargins(0, 0, 0, 0)
        layout_temperatures_FOG.addItem(self.temperature_FOG_x)
        layout_temperatures_FOG.addItem(self.temperature_FOG_y)
        layout_temperatures_FOG.addItem(self.temperature_FOG_z)

        layout.nextRow()

        layout_temperatures_AB = layout.addLayout(border=(100, 100, 100))
        layout_temperatures_AB.setContentsMargins(0, 0, 0, 0)
        layout_temperatures_AB.addItem(self.temperature_AB_x)
        layout_temperatures_AB.addItem(self.temperature_AB_y)
        layout_temperatures_AB.addItem(self.temperature_AB_z)
        layout.nextRow()

        self.setCentralItem(layout)

    def com_ports_changed(self):
        if self.com_ports.count() > 0:
            self.connect_btn.setEnabled(True)

    def on_connect_clicked(self):
        self.connection.connect()
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.reconnect_btn.setEnabled(True)
        self.timer.timeout.connect(self.update_graphics)
        self.timer.start(500)

    def on_disconnect_clicked(self):
        self.connection.disconnect()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.reconnect_btn.setEnabled(False)
        self.timer.stop()

    def on_reconnect_clicked(self):
        self.connection.reconnect()
        self.on_connect_clicked()

    def update_graphics(self):
        values = self.connection.get_output_data()
        self.angular_velocity_x.update(values[1])
        self.angular_velocity_y.update(values[2])
        self.angular_velocity_z.update(values[3])
        self.acceleration_x.update(values[4])
        self.acceleration_y.update(values[5])
        self.acceleration_z.update(values[6])
        if values[7] == 0:
            self.temperature_FOG_x.update(values[8])
        elif values[7] == 1:
            self.temperature_FOG_y.update(values[8])
        elif values[7] == 2:
            self.temperature_FOG_z.update(values[8])
        elif values[7] == 3:
            self.temperature_AB_x.update(values[8])
        elif values[7] == 4:
            self.temperature_AB_y.update(values[8])
        elif values[7] == 5:
            self.temperature_AB_z.update(values[8])

    def closeEvent(self, event):
        self.connection.stop_event.set()
        self.connection.connection_thread.join()
        self.connection.disconnect()
        event.accept()


if __name__ == '__main__':
    app = pg.mkQApp("Monitoring data from Block of Sensitive Sensors")
    monitoring_app = MonitoringApp()
    monitoring_app.show()
    pg.exec()
