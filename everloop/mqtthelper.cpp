#include <iostream>
#include <string>
#include "MQTTClient.h"
#include "mqtthelper.h"

volatile int msg = 0;
MQTTClient_deliveryToken deliveredtoken;


int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message)
{
  
    /*printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: ");
    msg = *((int*) message->payload);
    putchar('\n');
   */
   msg = std::stoi((char*)message->payload);
   //std::cout<<msg<<std::endl;
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
  MQTTClient client;
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
  std::cout<<"[Everloop]:  Connected<<std::endl";
  //printf("Subscribing to topic %s\nfor client %s using QoS%d\n\n", TOPIC, CLIENTID, QOS);
  MQTTClient_subscribe(client, TOPIC, QOS);


}
