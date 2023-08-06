from Gramophone import Gramophone
from time import time, sleep
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget
import sys

class Receiver(QWidget):
    def __init__(self, gram):
        super().__init__()
        self.gram = gram
        # self.gram.transmitter.position_signal.connect(self.print_pos)
        # self.gram.transmitter.velocity_signal.connect(self.print_vel)
        self.gram.transmitter.position_diff_signal.connect(self.print_dpos)

    @pyqtSlot(int)
    def print_dpos(self, stuff):
        print('dPOS: ', str(stuff))
        
    @pyqtSlot(int)
    def print_pos(self, stuff):
        print('POS: ', str(stuff))

    @pyqtSlot(float)
    def print_vel(self, stuff):
        print('VEL: ', str(stuff))

if __name__ == '__main__':
    devs = Gramophone.find_devices()
    print('First device:', devs[0].product_serial)
    print('First device:', hex(devs[0].product_serial))
    gram = Gramophone(devs[0], verbose=True)
    gram.open()

    sleep(1)
    gram.ping()
    # print()

    gram.read_product_info()
    gram.read_firmware_info()
    print('App state:', gram.app_state)
    # gram.check_app()
    # gram.reset()
    # print()

    # gram.write_param(0xD0, [1,2,3,4])
    # gram.read_param(0xD0)

    # for T in range(100):
    #     gram.read_param(0x11)
    #     sleep(0.5)

    # for I in range(10):
    #     gram.write_param(0x30, [1])
    #     sleep(0.1)
    #     gram.write_param(0x30, [0])
    #     sleep(0.1)

    # gram.read_input(1)
    # gram.read_inputs()
    # gram.read_output(2)
    # gram.read_outputs()

    # import numpy as np

    # wave = np.linspace(0, 2*np.pi, 1000)
    # wave = np.sin(wave)

    # for w in wave:
    #     gram.write_param(0x40, [w])

    # sleep(1)
    # until = time()+60
    # while time() < until:
    #     # gram.read_position()
    #     gram.read_velocity()
    #     sleep(0.1)
        # gram.read_inputs()

    app = QApplication([])
    rec = Receiver(gram)
    gram.write_param(0x10, [0x00, 0x00, 0x00, 0x00])

    gram.read_sensors()
    print(gram.sensor_values)
    # gram.start_reader('Slow vel', 'velocity', 10)
    # gram.start_reader('Fast pos', 'position', 0.1)
    gram.start_reader('asd', 'position', 10)

    rec.show()
    
    sys.exit(app.exec_())

    gram.stop_reader('asd')
    # gram.stop_reader('Fast pos')

    gram.close()
