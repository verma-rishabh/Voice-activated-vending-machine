#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes, MqttOptions
import io
import sys
from threading import Thread
import json
import csv
import datetime
import paho.mqtt.client as mqtt_client

CONFIG_MENU = "menu.json"
CONFIG_ORDER = "orders.csv"
CURRENT_ORDER_ID = 001
CURRENT_CUSTOMER_ID = 001
USER_FILE = "user.json"



class order(object):
    def __init__(self,userid,orderid_):

        self.state = -1
        self.order = {}
        self.orderID = orderid_
        self.customerID = userid
        self.lastDialogue = ""
        self.orderCost = 0
        self.allergies = []
        self.instructions = []
        self.loaduserData()

    def loaduserData(self):
        try:
            self.allergies.append(kiosk.user[self.customerID]["allergies"])
        except:
            pass

    def repeatLastOrder(self):
        order_ = self.allergies.append(kiosk.user[self.customerID]["lastOrder"])
        dialogue = ""
        if order:
            self.order = order_
            dialogue = self.reciteOrder()
        else:
            dialogue = "I can't find your old order, but you can always make \
            a new one. "
    # mqtt callback after recieving payment status from nfc card reader.

    def payment_status_callback(self,msg):

        dialogue = ""
        if int(msg.payload) == 0:
            self.state = 8
            dialogue = " Sorry your order cannot be processed. "
            kiosk.mqtt.publish("everloop","3")
        elif int(msg.payload) ==1:
            dialogue = " Thank you for your order. "
            self.state = 7
            kiosk.mqtt.publish("everloop","3")

        self.lastDialogue = dialogue

    # generates text to be displayed on the GUI
    def guiText(self):
        cost = 0
        s="OrderID: " + str(self.orderID) + " " + "\n"
        for item,amount in self.order.items():
            s += str(amount) +"    x    " +  str(item) + "\n"
            cost += kiosk.menu[item] * amount

        s +=  str(cost) + "    ==    Total \n"
        s += "Allergies     : " + str(self.allergies) + "\n"
        s += "Instructions  : " + str(self.instructions) + "\n"
        return s

    # this function is called if face of this user is detected or
    def face_detection_callback(self,msg):

        dialogue = ""
        if self.state == 9:
            self.state = 10
        return dialogue

    def payment(self):
        kiosk.mqtt.publish("everloop","4")
        kiosk.mqtt.publish("payment/start",self.orderCost)

    def vending(self):
        pass


    def deliver(self):

        kiosk.mqtt.publish("motors",2)
        kiosk.mqtt.publish("motors",1)
        self.state = 11



    def checkForAllergies(self):
        dialogue = "I have noticed "
        count = 0
        for item in self.order.keys():
            for allergy in self.allergies:
                if allergy in kiosk.ingredients[item]:
                    dialogue = str(item) + " contain " + str(allergy)
                    count +=1
        if count >0:
            return dialogue
        else:
            return ""

    def calOrder(self):
        self.orderCost = 0
        for item,amount in self.order.items():
            self.orderCost += kiosk.menu[item] * amount

    def writeOrderFile(self):
        time_stamp = datetime.datetime.now()
        with open(CONFIG_ORDER, 'a') as f:
            for item,quantity in self.order.items():
                fields=[time_stamp,self.orderID,self.customerID,item,quantity]
                writer = csv.writer(f)
                writer.writerow(fields)

    def writeUserFile(self):
        if self.customerID in kiosk.user.keys():
            kiosk.user[self.customerID]["lastOrder"] = self.order
            kiosk.user[self.customerID]["allergies"] = self.allergies
        else:
            d = {"customerID": self.customerID, "lastOrder" : self.order,
             "allergies": self.allergies}
            kiosk.user[self.customerID] = d
        with open('user.json', 'w') as json_file:
            json.dump(kiosk.user, json_file)

    def orderCompleted(self):

        self.writeOrderFile()
        self.writeUserFile()





    def reciteOrder(self):
        dialogue = "Your order contains "
        for i in self.order.items():
            dialogue += str(i[1]) +" " +  str(i[0])
        return dialogue

    def finaliseOrder(self):
        dialogue = self.reciteOrder()
        self.calOrder()

        dialogue += ". Your order cost " + str(self.orderCost) \
        + " Please proceed to payment"

        return dialogue


    def addAllergies(self,intent_message):
        allergies_l= []

        for name,values in intent_message.slots.items():
            if name == "allergies":
                allergies_l = list(map(lambda x: str(x.value), values.all()))


        dialogue = ""
        for a in allergies_l:
            self.allergies.append(a)
            dialogue += " " + str(a)

        dialogue += " is added. "
        allergyAlert = self.checkForAllergies()
        if(allergyAlert):
            dialogue += allergyAlert
            self.state = 3

        else:
            self.state = 4

        return dialogue

    # -> action callbacks
    def addItems(self, intent_message):

        #print ("[Received] intent: {}".format(intent_message.intent.intent_name))
        for name,values in intent_message.slots.items():
            if name == "item":
                items = list(map(lambda x: str(x.value), values.all()))

            if name == "amount":
                amount = list(map(lambda x: int(x.value), values.all()))


        try:
            if len(items) == len(amount):
                add = {}
                add = dict(zip(items,amount))

                dialogue = ""

                for dish,amount in add.items():
                    if dish in self.order.keys():
                        self.order[dish] = self.order[dish] + amount
                    else:
                        if dish in kiosk.menu.keys():
                            self.order[dish] = amount
                            dialogue += str(amount) +" " +  str(dish)


                dialogue += " is added to your order. "


            else:
                dialogue = " Sorry, please use numbers for quantity. "




        except:
            dialogue =  " Sorry, I didn't get that. "

        self.state = 0;


        return dialogue



    def removeItems(self,intent_message):
        for name,values in intent_message.slots.items():
            if name == "item":
                items = list(map(lambda x: str(x.value), values.all()))

            if name == "amount":
                amount = list(map(lambda x: int(x.value), values.all()))
        p= []
        try:
            p = map(lambda x: self.order.pop(x,""),items)
        except:
            pass
        dialogue=""
        count=0
        for i in range(len(p)):
            if p[i]:
                count += 1
                dialogue+= " " + str(item[i]) + ", "
        if count == 1:
            dialogue+=" is removed from your order "
        if count  > 1:
            dialogue+=" are removed from your order "

        if count == 0:
            dialogue = " Nothing to remove, "

        self.state = 0

        return dialogue


    def suggestion(self,intent_message):
        pass
#        for name,values in intent_message.slots.items():
#            if name == "menuSection":
#                section_l = list(map(lambda x: str(x.value), values.all()))

 #       dialogue = ""

#        for section in section_l:
#            dialogue += "our top 3 items in" + section + "are" \
#            + suggestion_list[section][0] +" " + suggestion_list[section][1]\
#            + "and" + suggestion_list[section][2]

#        self.state = 0

#        return dialogue

    def removeAllergicItems(self):
        for item in self.order.keys():
            for allergy in self.allergies:
                if allergy in kiosk.ingredients[item]:
                    self.order.pop(item)

    def addInstructions(self,intent_message):
        instructions_l = []
        dialogue = ""
        for name,values in intent_message.slots.items():
            if name == "specialRequest":
                instructions_l = list(map(lambda x: str(x.value), values.all()))

        for i in instructions_l:
            self.instructions.append(i)
            dialogue += str(i)
        self.state = 6
        dialogue += "is added."

        return dialogue

    def response(self,intent_message):
        for name,values in intent_message.slots.items():
            if name == "response":
                response = list(map(lambda x: str(x.value), values.all()))
        dialogue = ""

        if self.state == 0:
            if "no" in response:
                self.state =  1

            else:
                self.state = 0
                dialogue = " Please specify your order in items and quantity "

        elif self.state == 1:
            if "no" in response:
                self.state = 4

            else:
                self.state = 2


        elif self.state == 3:
            self.state = 4
            if "yes" in response:
                self.removeAllergicItems()

        elif self.state == 4:
            if "yes" in response:
                self.state = 5
            else:
                self.state = 6

        return dialogue


    def order_intent_callback(self,hermes,intent_message):

        print ("[Received] intent: {}".format(intent_message.intent.intent_name))

        if intent_message.intent.intent_name == "verma-rishabh:addItems":
            self.lastDialogue = self.addItems(intent_message)

        if intent_message.intent.intent_name == "verma-rishabh:removeItems":
            self.lastDialogue = self.removeItems(intent_message)

        if intent_message.intent.intent_name == "verma-rishabh:suggestion":
            self.lastDialogue = self.suggestion(intent_message)

        if intent_message.intent.intent_name == "verma-rishabh:response":
            self.lastDialogue = self.response(intent_message)

        if intent_message.intent.intent_name == "verma-rishabh:allergies":
            self.lastDialogue = self.addAllergies(intent_message)

        if intent_message.intent.intent_name == "verma-rishabh:specialRequest":
            self.lastDialogue = self.addInstructions(intent_message)

        self.stateSpace(hermes,intent_message)

    def stateSpace(self,hermes,intent_message):
        kiosk.mqtt.publish("everloop","0")

        if self.state == 0:
            self.lastDialogue += " Would you like to edit your order or continue?"
            hermes.publish_continue_session(intent_message.session_id,\
            self.lastDialogue ,
            ["verma-rishabh:response","verma-rishabh:addItems",\
            "verma-rishabh:removeItems",\
            "verma-rishabh:suggestion"],"")
            kiosk.mqtt.publish("everloop","1")


        elif self.state == 1:
            self.lastDialogue += " Would you like to add any allergies?"
            hermes.publish_continue_session(intent_message.session_id,\
            self.lastDialogue ,\
            ["verma-rishabh:response","verma-rishabh:allergies"],"")
            kiosk.mqtt.publish("everloop","1")


        elif self.state == 2:
            self.lastDialogue += " Please state your allergies"
            hermes.publish_continue_session(intent_message.session_id,\
            self.lastDialogue ,\
            ["verma-rishabh:allergies"],"")
            kiosk.mqtt.publish("everloop","1")


        elif self.state == 3:
            self.lastDialogue += " Would you like to remove these items?"
            hermes.publish_continue_session(intent_message.session_id,\
            self.lastDialogue ,\
            ["verma-rishabh:response"],"")
            kiosk.mqtt.publish("everloop","1")

        elif self.state == 4:
            self.lastDialogue += " Would you like to add any instructions?"
            hermes.publish_continue_session(intent_message.session_id,\
            self.lastDialogue ,\
            ["verma-rishabh:specialRequest","verma-rishabh:response"],"")

        elif self.state == 5:
            self.lastDialogue += " Please state your instructions"
            hermes.publish_continue_session(intent_message.session_id,\
            self.lastDialogue ,\
            ["verma-rishabh:specialRequest"],"")
            kiosk.mqtt.publish("everloop","1")

        elif self.state == 6:
            self.lastDialogue = self.finaliseOrder()
            self.lastDialogue += " Please place your card near the reader"
            hermes.publish_end_session(intent_message.session_id,\
            self.lastDialogue)
            self.payment()
            kiosk.mqtt.publish("everloop","4")

        elif self.state == 7:
            self.lastDialogue += " Your orderid is " + str(self.orderID)
            hermes.publish_start_session_notification("default",\
            self.lastDialogue,"")
            kiosk.mqtt.publish("everloop","0")


            self.orderCompleted()
            text = self.guiText()
            kiosk.mqtt.publish("guiBack/text",text)

        elif self.state == 8:
            self.lastDialogue += ""
            hermes.publish_start_session_notification("default",\
            self.lastDialogue,"")
            kiosk.mqtt.publish("everloop","0")


        elif self.state == 9:

            self.lastDialogue = "Order number " + str(self.orderID) \
            + " please collect your order"

            hermes.publish_start_session_notification("default",\
            self.lastDialogue,"")
            kiosk.mqtt.publish("everloop","0")



        elif self.state == 10:
            print ("[Kiosk] : delivering Order")
            self.deliver()
#TODO for idle everloop

        text = self.guiText()
        kiosk.mqtt.publish("guiFront/text",text)

        #print (self.dialogue)

class kiosk(object):

    def on_connect(self,client, userdata, flags, rc):
        print('[Kiosk] : Connected')
        kiosk.mqtt.subscribe("payment/status")
        kiosk.mqtt.subscribe("camera/recognisedIds")
        kiosk.mqtt.subscribe("guiBack/completedOrder")


    def __init__(self):
        self.mqtt_addr = "raspberrypi.local:1883"
        kiosk.currentOrder=[]
        self.newFace = 0
        kiosk.menu = self.loadMenu()
        kiosk.ingredients = self.loadingredients()
        kiosk.user = self.loadUserFile()
        kiosk.mqtt = mqtt_client.Client()

        self.loadMqtt()
        self.start_blocking()



    def loadMqtt(self):

        kiosk.mqtt.on_connect = self.on_connect
        kiosk.mqtt.on_message = self.mqtt_callback
        kiosk.mqtt.connect('raspberrypi.local', 1883)
        kiosk.mqtt.loop_start()

    def loadMenu(self):
        menuDict = {}
        with open(CONFIG_MENU) as config_menu_file:
            menu=json.load(config_menu_file)
            for section in menu.values():

                map(lambda x,y: menuDict.update({x:y["price"]}),
                section[0].keys(),section[0].values())

        return menuDict


    def loadingredients(self):
        allergiesDict = {}
        with open(CONFIG_MENU) as config_allergies_file:
            menu=json.load(config_allergies_file)
            for section in menu.values():

                map(lambda x,y: allergiesDict.update({x:y["ingredients"]}),
                section[0].keys(),section[0].values())

        return allergiesDict


    def loadUserFile(self):
        with open(USER_FILE) as file:
            user=json.load(file)
        return user

    def newOrder(self):
        global CURRENT_ORDER_ID,CURRENT_CUSTOMER_ID
        if self.newFace != 0:
            userid = self.newFace
        else:
            userid = CURRENT_CUSTOMER_ID
            CURRENT_CUSTOMER_ID +=1
            print("adding new face ")
            kiosk.mqtt.publish("camera/addId",userid)

        kiosk.currentOrder.append(order(userid,CURRENT_ORDER_ID))
        CURRENT_ORDER_ID +=1

    def master_intent_callback(self, hermes, intent_message):
        #if latest order is already completed start new one
        if not kiosk.currentOrder:
            self.newOrder()
            kiosk.mqtt.publish("guiFront/text","")
            kiosk.currentOrder[-1].order_intent_callback(hermes, intent_message)

        elif kiosk.currentOrder[-1].state> 6:
            self.newOrder()
            kiosk.mqtt.publish("guiFront/text","")
            kiosk.currentOrder[-1].order_intent_callback(hermes, intent_message)

        else:
            kiosk.currentOrder[-1].order_intent_callback(hermes, intent_message)

# mqtt callbacks

    def mqtt_callback(self,client, userdata, msg):
        with Hermes() as hermes:

        #    print ("mqtt reciever" + msg.topic)

            if msg.topic == "payment/status":
                print("[payment status] : " + str (msg.payload))
                kiosk.currentOrder[-1].payment_status_callback(msg)
                kiosk.currentOrder[-1].stateSpace(hermes,msg)

            if msg.topic == "camera/recognisedIds":
                ids = list(map(int,msg.payload.split()))
                print ("[face detected] : " + str(ids))

                for user in kiosk.currentOrder:

                    if user.customerID in ids:
                        user.face_detection_callback(msg)
                        if user.state == 10:
                            user.stateSpace(hermes,msg)
                        ids.remove(user.customerID)
                # if new face, save it in self.newFace.
                if ids:
                    ids.sort()                                                  #makes sure we get non 0 id if present
                    self.newFace = ids[-1]


            if msg.topic == "guiBack/completedOrder":
                print("[Order Completed")
                for user in kiosk.currentOrder:
                    if user.orderID == int(msg.payload) and user.state == 7:
                        user.state = 9


                        user.stateSpace(hermes,msg)






# subscribing to snips intents
    def start_blocking(self):

        with Hermes(self.mqtt_addr) as h:
            h.subscribe_intents(self.master_intent_callback).start()


if __name__ == "__main__":

    kiosk()
