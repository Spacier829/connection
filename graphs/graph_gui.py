import numpy as np
import pyqtgraph as pg


class graph_gui(pg.PlotItem):

    def __init__(self, parent=None, name=None, labels=None,
                 title=None, viewBox=None, axisItems=None,
                 enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems,
                         enableMenu, **kargs)
        self.graph_plot = self.plot(pen=(255, 255, 255))
        self.graph_data = np.linspace(0, 0, 10)
        self.ptr1 = 0

    def set_title(self, title):
        self.setTitle(title)

    def update(self, value):
        self.graph_data[:-1] = self.graph_data[1:]
        self.graph_data[-1] = float(value)
        self.ptr1 += 1
        self.graph_plot.setData(self.graph_data)
        self.graph_plot.setPos(self.ptr1, 0)
