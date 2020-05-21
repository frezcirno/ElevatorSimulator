#!/usr/bin/python
# -*- coding: utf-8 -*-
''' MVC中的C '''
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from EView import EView
from EModel import EModel, state_t


class EController(QtWidgets.QDialog):
    def __init__(self):
        super(EController, self).__init__()
        self.ui = EView()
        self.ui.setupUi(self)
        self.setupSlot()
        self.model = EModel()

        self.timer = QtCore.QBasicTimer()
        self.timer.start(1000, self)

        class OutputStream(QtCore.QObject):
            on_print = QtCore.pyqtSignal(str)

            def write(self, text):
                self.on_print.emit(text)

            def flush(self):
                pass

        sys.stdout = OutputStream(on_print=lambda text: self.ui.logger.insertPlainText(text))

    def __del__(self):
        sys.stdout = sys.__stdout__

    def timerEvent(self, event):
        self.model.update()
        self.ui_update()

    def ui_update(self):
        for i in range(20):
            EController.setButtonState(getattr(self.ui, 'up_'+str(i)), self.model.up[i])
            EController.setButtonState(getattr(self.ui, 'down_'+str(i)), self.model.down[i])

        for e in range(5):
            level = self.model.level[e]
            status = self.model.status[e]

            slider = getattr(self.ui, 'slider_'+str(e))
            EController.setSliderState(slider, status)
            EController.setSliderValue(slider, level)

            getattr(self.ui, 'lcd_'+str(e)).display(str(level+1) if status != state_t.STAT_DISABLED else 'Er')
            getattr(self.ui, 'elev_'+str(e)+'_lcd').display(str(level+1) if status != state_t.STAT_DISABLED else 'Er')

            for i in range(20):
                EController.setButtonState(getattr(self.ui, 'elev_'+str(e)+'_'+str(i)), self.model.goto[e][i])

    def setupSlot(self):
        for index in range(20):
            getattr(self.ui, 'up_'+str(index)).clicked.connect(lambda b, _i=index: self.on_updown_clicked(0, _i))
            getattr(self.ui, 'down_'+str(index)).clicked.connect(lambda b, _i=index: self.on_updown_clicked(1, _i))

        for e in range(5):
            getattr(self.ui, 'elev_'+str(e)+'_repair').clicked.connect(lambda b, _e=e: self.on_repair_clicked(_e))
            getattr(self.ui, 'elev_'+str(e)+'_open').clicked.connect(lambda b, _e=e: self.on_open_clicked(_e))
            getattr(self.ui, 'elev_'+str(e)+'_close').clicked.connect(lambda b, _e=e: self.on_close_clicked(_e))
            for i in range(20):
                getattr(self.ui, 'elev_'+str(e)+'_'+str(i)).clicked.connect(lambda b, _e=e, _i=i:
                                                                            self.on_goto_clicked(_e, _i))

    # Slots
    def on_updown_clicked(self, isdown, index):
        print('%d楼发出向%s请求' % (index+1, '下' if isdown else '上'))
        upordown = (self.model.down if isdown else self.model.up)
        upordown[index] = 1
        button = getattr(self.ui, ('down_' if isdown else 'up_')+str(index))
        EController.setButtonState(button, True)

    def on_goto_clicked(self, elevNo, index):
        print('%d号电梯请求去%d楼' % (elevNo+1, index+1))
        self.model.goto[elevNo][index] = 1
        EController.setButtonState(getattr(self.ui, 'elev_'+str(elevNo)+'_'+str(index)), True)

    def on_repair_clicked(self, elevNo):
        print('%d号电梯%s使用' % (elevNo+1, '恢复' if self.model.disable[elevNo] else '停止'))
        self.model.disable[elevNo] = 1-self.model.disable[elevNo]
        EController.setButtonState(getattr(self.ui, 'elev_'+str(elevNo)+'_repair'), self.model.disable[elevNo])

    def on_open_clicked(self, elevNo):
        print('%d号电梯请求开门' % (elevNo+1))
        self.model.wait[elevNo] = 8
        EController.setButtonState(getattr(self.ui, 'elev_'+str(elevNo)+'_open'), False)

    def on_close_clicked(self, elevNo):
        print('%d号电梯请求关门' % (elevNo+1))
        self.model.wait[elevNo] = 3
        EController.setButtonState(getattr(self.ui, 'elev_'+str(elevNo)+'_close'), False)

    @staticmethod
    def setButtonState(button: QtWidgets.QPushButton, b):
        button.setChecked(b)

    @staticmethod
    def setSliderValue(slider, value):
        slider.setValue(value)

    @staticmethod
    def setSliderState(slider, state):
        if state == state_t.STAT_DOCKING:
            slider.setStyleSheet("QSlider::handle {\n"
                                 "background: red;\n"
                                 "}")
        elif state == state_t.STAT_UP or state == state_t.STAT_DOWN:
            slider.setStyleSheet("QSlider::handle {\n"
                                 "background: yellow;\n"
                                 "}")
        elif state == state_t.STAT_DISABLED:
            slider.setStyleSheet("QSlider::handle {\n"
                                 "background: grey;\n"
                                 "}")
        else:  # 无操作,等待
            slider.setStyleSheet("QSlider::handle {\n"
                                 "background: green;\n"
                                 "}")
