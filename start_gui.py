from multiprocessing import Process, Queue
from time import sleep, time
from random import randint
import sys
import run_model
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

#import run_model


class MyCustomWindow(QMainWindow):
    def __init__(self):
        self.queue = Queue()
        super(MyCustomWindow, self).__init__()
        self.setGeometry(1080, 720, 1080, 720)
        self.setWindowTitle("Image restoration")
        self.setAcceptDrops(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)

        self.initUI()

    def initUI(self):
        self.labeled = QtWidgets.QLabel(self)
        self.labeled.hide()

        self.button2 = QPushButton(self)
        self.button2.hide()
        self.button3 = QPushButton(self)
        self.button3.hide()

        self.label = QtWidgets.QLabel(self)
        self.label.setText("Image Restoration")
        self.label.move(320, 30)
        self.label.setFixedSize(500, 100)
        self.label.setStyleSheet("font-size: 50px; font-weight: bold; font-family: Inter; color: #6D9886;")

        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText("To upload your image.")
        self.label2.move(470, 300)
        self.label2.setFixedSize(250, 50)
        self.label2.setStyleSheet("font-size: 20px; font-weight: bold; font-family: Inter; color: #393E46;")

        self.button = QPushButton(self)
        self.button.setText("Click me")
        self.button.move(360, 300)
        self.button.setStyleSheet("font-size: 20px; font-weight: bold; font-family: Inter; color: #F2E7D5; background-color: #393E46; border-radius: 10px;")
        self.button.setFixedSize(100, 50)
        self.button.clicked.connect(self.open_image)

        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText("Or simply drag and drop your image here.")
        self.label3.move(380, 340)
        self.label3.setFixedSize(300, 50)
        self.label3.setStyleSheet("font-size: 13px; font-family: Inter; color: #393E46;")

        # Start Animation
    def update_label(self):
        
        phrases = ["                                      Go grab a snack while we do some stuff.                                ",
                   "                        In the meantime, feel free to count the pixels on your screen.                       ",
                   "While you wait, see if you can guess the loading time down to the second... or give up and make some popcorn.",
                   "      While you wait, try to find the hidden message in the loading screen... or just make up your own.      ",
                   "                            This may take some time. or not, depends on the mood.                            ",
                   "                           Don't worry, the image is just getting a digital makeover.                        ",
                   "                   If your fan started working you may wanna take a break and comeback later.                ",
                   "                              If you buy a GPU it will make both our lifes easier...                         "
                   ]
        self.label2.setText(phrases[randint(0, len(phrases)-1)])

        if not self.queue.empty():
            # stop
            self.stopAnimation()
            self.timer.stop()
            self.show_end_screen()


    def show_end_screen(self):
        self.label3.setText("Done!")
        self.label2.setText("                               Your image is ready and saved to output.png")
        self.labeled.hide()


    def startAnimation(self):
        self.movie.start()

    # Stop Animation(According to need)
    def stopAnimation(self):
        self.movie.stop()


    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            filename = event.mimeData().urls()[0].toLocalFile()
            event.accept()
            self.open_image(filename)
        else:
            event.ignore()

    def open_image(self, filename=None):
        
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
        if filename:
            self.filename = filename
            self.loaded_image()

    def loaded_image(self):
        self.setAcceptDrops(False)
        print(self.filename)
        self.label2.hide()

        self.button.setText("Change image")
        self.button.move(380, 480)
        self.button.setFixedSize(250, 50)
        #self.button.hide()

        self.button2 = QPushButton(self)
        self.button2.setText("Denoise image")
        self.button2.move(380, 320)
        self.button2.setFixedSize(250, 50)
        self.button2.setStyleSheet("font-size: 20px; font-weight: bold; font-family: Inter; color: #F2E7D5; background-color: #393E46; border-radius: 10px;")
        self.button2.show()
        self.button2.clicked.connect(lambda: self.start_treatement("denoise"))
        
        self.button3.setText("Deblur image")
        self.button3.move(380, 400)
        self.button3.setFixedSize(250, 50)
        self.button3.setStyleSheet("font-size: 20px; font-weight: bold; font-family: Inter; color: #F2E7D5; background-color: #393E46; border-radius: 10px;")
        self.button3.show()
        self.button3.clicked.connect(lambda : self.start_treatement("deblur"))


        self.label3.setText("Loaded image: " + self.filename)
        self.label3.setStyleSheet("font-size: 17px; font-weight: bold; font-family: Inter; color: #393E46;")
        self.label3.setFixedSize(500, 50)
        self.label3.move(300, 260)


    def treat_image(self, target):

        output = "output.png"
        self.queue.put(run_model.main(self.filename, output, target))



        




    def start_treatement(self, target):
        # sends a process to treat the image 

        self.timer.start(5000)

        if __name__ == "__main__":  # confirms that the code is under main function

            proc = Process(target=self.treat_image, args=(target,))
            proc.start()


        # here shows the loading screen
        self.button.hide()
        self.button2.hide()
        self.button3.hide()

        self.label3.move(490, 350)
        self.label3.setStyleSheet("font-size: 20px; font-weight: bold; font-family: Inter; color: #393E46;")
        self.label3.setText("Working...")

        self.label2.show()
        self.label2.move(270, 400)
        self.label2.setFixedSize(700, 30)
        self.label2.setStyleSheet("font-size: 13px; font-family: Inter; color: #393E46;")
        self.label2.setText("                                      Operation started successfully.                                  ")

        
            # Loading the GIF
        self.labeled.show()
        self.labeled.setFixedSize(200, 200)
        self.labeled.move(440, 200)
        self.movie = QMovie("loader.gif")
        self.labeled.setMovie(self.movie)
        self.startAnimation()


        


def show_window():
    app = QApplication(sys.argv)
    win = MyCustomWindow()

    win.show()

    sys.exit(app.exec_())


show_window()
