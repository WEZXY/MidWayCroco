#!/home/elmoslimany/ros2_ws/src/.venv/bin/python
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLabel, QSpinBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Random Numbers')
        self.initUI()
        
    def initUI(self):
        self.label = QLabel(f'Random Numbers: {0}')

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def generate(self):
        pass

    # def closeEvent(self, event):
    #     self.ros_thread.quit()
    #     self.ros_thread.wait()


def main(args=None):

    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()