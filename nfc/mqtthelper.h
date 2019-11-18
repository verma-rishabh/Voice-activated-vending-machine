#ifndef MQTTHELPER_H
#define MQTTHELPER_H


#include "MQTTClient.h"


#define TIMEOUT     10000L

extern volatile double msg;
extern MQTTClient_deliveryToken deliveredtoken;
int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message);
void delivered(void *context, MQTTClient_deliveryToken dt);
void connlost(void *context, char *cause);
void initMqtt(char *ADDRESS,char *CLIENTID,char *TOPIC,int QOS);
void publishStatus(char *topic,char *payload);
#endif
