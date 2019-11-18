import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import paho.mqtt.client as mqtt

#import paho.mqtt.client as mqtt




def on_connect(client, userdata, flags, rc):
    print("[Menu]: Connected ")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("guiFront/text")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    l1.setText((msg.payload))
   # l1.repaint()
    
def initMqtt():
   client = mqtt.Client()
   client.on_connect = on_connect
   client.on_message = on_message
   client.connect("localhost", 1883, 60)
   client.loop_start()

def window():
   window = QWidget()
   hbox = QHBoxLayout()
   menu = QLabel()
   menu.setPixmap(QPixmap("menu.jpg"))
   hbox.addWidget(menu)
   hbox.addStretch()
   hbox.addWidget(l1)
   hbox.addStretch()
   window.setWindowTitle("MENU")
   window.setLayout(hbox)
   window.show()
   window.setLayout(hbox)
   sys.exit(app.exec_())



if __name__ == '__main__':
   initMqtt()
   app = QApplication(sys.argv)
   l1=QLabel()
   window()
