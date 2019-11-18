#include <iostream>
#include <string.h>
#include "MQTTClient.h"
#include "mqtthelper.h"

volatile double msg = 0;
MQTTClient_deliveryToken deliveredtoken;
  MQTTClient client;
  MQTTClient_message pubmsg = MQTTClient_message_initializer;
  MQTTClient_deliveryToken token;

int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message)
{

    /*printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: ");
    putchar('\n');

   */
   //std::cout<<(char*)message->payload;
   msg = std::stod((char*)message->payload);

    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);


    return 1;
}
void delivered(void *context, MQTTClient_deliveryToken dt)
{
    deliveredtoken = dt;
}

void connlost(void *context, char *cause)
{
    printf("\n[Everloop]:  Connection lost\n");
    printf("     cause: %s\n", cause);
}
void initMqtt(char *ADDRESS,char *CLIENTID,char *TOPIC,int QOS){

  MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
  int rc;
  int ch;
  MQTTClient_create(&client, ADDRESS, CLIENTID,MQTTCLIENT_PERSISTENCE_NONE, NULL);
  conn_opts.keepAliveInterval = 20;
  conn_opts.cleansession = 1;
  MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered);
  if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
  {
      printf("[Everloop]:  Failed to connect, return code %d\n", rc);
      exit(EXIT_FAILURE);
  }
  std::cout<<"Vendong Machine]:  Connected"<<std::endl;
  //printf("Subscribing to topic %s\nfor client %s using QoS%d\n\n", TOPIC, CLIENTID, QOS);
  MQTTClient_subscribe(client, TOPIC, QOS);
}
void publishStatus(char *topic,char *payload){
  int rc;
   pubmsg.payload = payload;
   pubmsg.payloadlen = 1;
   pubmsg.qos = 0;
   pubmsg.retained = 0;
    deliveredtoken = 0;
    MQTTClient_publishMessage(client,topic, &pubmsg, &token);
    printf("Waiting for publication of %s\n"
            "on topic %s \n",
            payload, topic);
    while(deliveredtoken != token);
    printf("[paymentny]Message with delivery\n");
}
