import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import paho.mqtt.client as mqtt
from functools import partial

client = mqtt.Client()
count = 0




# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("guiBack/text")



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
        global count
        print(msg.topic+" "+str(msg.payload))
        s=str(msg.payload)
        label[count].setText((msg.payload))
        orderid = int(s.split(" ")[1])
        print orderid
        button[count].setText('Completed')
        head[count].setText(str(orderid))
        count +=1


def initMqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("raspberrypi.local", 1883, 60)
    client.loop_start()

def clicked(i):
    client.publish("guiBack/completedOrder",str(head[i].text()))
    label[i].setText('')
    button[i].setText('')
    head[i].setText('')
def screen():
    vbox = QVBoxLayout()
    window = QWidget()
    h1 = QLabel('Cafe')
    h1.setStyleSheet("font: 30pt Comic Sans MS")
    h1.setAlignment(Qt.AlignCenter)
    vbox.addWidget(h1)
    vbox.addStretch()
    for i in range(5):
        vbox.addWidget(head[i])
        vbox.addStretch()
        vbox.addWidget(label[i])
        vbox.addStretch()
        vbox.addWidget(button[i])
        vbox.addStretch()

        head[i].setStyleSheet("font: 10pt Comic Sans MS")
        button[i].clicked.connect(partial(clicked,i))
        window.setLayout(vbox)
    window.setWindowTitle("Kitchen")
    window.setLayout(vbox)
    window.show()

    sys.exit(app.exec_())




if __name__ == '__main__':

   initMqtt()
   app = QApplication(sys.argv)
   label=[]
   button = []
   head = []
   for i in range(5):
       label.append(QLabel(""))
       button.append(QPushButton(""))
       head.append(QLabel(""))

   screen()
