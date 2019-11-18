

// System calls
#include <unistd.h>
// Input/output streams and functions
#include <iostream>
// Included for sin() function.
#include <cmath>

#include "mqtthelper.h"
// Interfaces with Everloop
#include "matrix_hal/everloop.h"
// Holds data for Everloop
#include "matrix_hal/everloop_image.h"
// Communicates with MATRIX device
#include "matrix_hal/matrixio_bus.h"

char ADDRESS[] = "localhost:1883";
char CLIENTID[] = "everloop";
char TOPIC[] = "everloop";
int QOS =  0;


float counter = 0;
// const float freq = 0.375;
const float freq = 0.375;





typedef struct {
    double r;       // a fraction between 0 and 1
    double g;       // a fraction between 0 and 1
    double b;       // a fraction between 0 and 1
} rgb;

typedef struct {
    double h;       // angle in degrees
    double s;       // a fraction between 0 and 1
    double v;       // a fraction between 0 and 1
} hsv;

hsv color_hsv;
rgb color_rgb;

hsv rgb2hsv(rgb in)
{
    hsv         out;
    double      min, max, delta;

    min = in.r < in.g ? in.r : in.g;
    min = min  < in.b ? min  : in.b;

    max = in.r > in.g ? in.r : in.g;
    max = max  > in.b ? max  : in.b;

    out.v = max;                                // v
    delta = max - min;
    if (delta < 0.00001)
    {
        out.s = 0;
        out.h = 0; // undefined, maybe nan?
        return out;
    }
    if( max > 0.0 ) { // NOTE: if Max is == 0, this divide would cause a crash
        out.s = (delta / max);                  // s
    }
    else {

             // if max is 0, then r = g = b = 0
        // s = 0, h is undefined
        out.s = 0.0;
        out.h = NAN;                            // its now undefined
        return out;
    }
    if( in.r >= max )                           // > is bogus, just keeps compilor happy
        out.h = ( in.g - in.b ) / delta;        // between yellow & magenta
    else
    if( in.g >= max )
        out.h = 2.0 + ( in.b - in.r ) / delta;  // between cyan & yellow
    else
        out.h = 4.0 + ( in.r - in.g ) / delta;  // between magenta & cyan

    out.h *= 60.0;                              // degrees

    if( out.h < 0.0 )
        out.h += 360.0;

    return out;
}


rgb hsv2rgb(hsv in)
{
    double      hh, p, q, t, ff;
    long        i;
    rgb         out;

    if(in.s <= 0.0) {       // < is bogus, just shuts up warnings
        out.r = in.v;
        out.g = in.v;
        out.b = in.v;
        return out;
    }
    hh = in.h;
    if(hh >= 360.0) hh = 0.0;
    hh /= 60.0;
    i = (long)hh;
    ff = hh - i;
    p = in.v * (1.0 - in.s);
    q = in.v * (1.0 - (in.s * ff));
    t = in.v * (1.0 - (in.s * (1.0 - ff)));

    switch(i) {
    case 0:
        out.r = in.v;
        out.g = t;
        out.b = p;
        break;
    case 1:
        out.r = q;
        out.g = in.v;
        out.b = p;
        break;
    case 2:
        out.r = p;
        out.g = in.v;
        out.b = t;
        break;

    case 3:
        out.r = p;
        out.g = q;
        out.b = in.v;
        break;
    case 4:
        out.r = t;
        out.g = p;
        out.b = in.v;
        break;
    case 5:
    default:
        out.r = in.v;
        out.g = p;
        out.b = q;
        break;
    }
    return out;
}






void pattern1(matrix_hal::EverloopImage everloop_image,matrix_hal::Everloop everloop)
{
  color_rgb.r = 15.0/255;
  color_rgb.g = 15.0/255;
  color_rgb.b = 125.0/255;
  color_hsv = rgb2hsv(color_rgb);

  for (int i = 0; i <=25; i++)
  {
    for (matrix_hal::LedValue &led : everloop_image.leds)
    {
      color_hsv.v = fmax(std::sin(freq*counter),0.05);
      color_rgb = hsv2rgb(color_hsv);
      led.red = (color_rgb.r*255.0);
      led.green = (color_rgb.g*255.0);
      led.blue = (color_rgb.b*255.0);
      counter = counter + 0.5;
    }
       everloop.Write(&everloop_image);
       if (i == 0) {
    // Output everloop status to console
    
    }
    // If i is cleanly divisible by 25
    //if ((i % 25) == 0) {
    //std::cout << "Time remaining (s) : " << 10 - (i / 25) << std::endl;
    //}
       usleep(40000);
  }


}
void pattern0(matrix_hal::EverloopImage everloop_image,matrix_hal::Everloop everloop)
{
  color_rgb.r = 15.0/255;
  color_rgb.g = 15.0/255;
  color_rgb.b = 125.0/255;
  color_hsv = rgb2hsv(color_rgb);
  for (int i = 0; i <=25; i++)
  {
    for (matrix_hal::LedValue &led : everloop_image.leds)
    {
      color_hsv.v = fmax(std::sin(freq),0.05);
      color_rgb = hsv2rgb(color_hsv);
      led.red = (color_rgb.r*255.0);
      led.green = (color_rgb.g*255.0);
      led.blue = (color_rgb.b*255.0);

    }
    everloop.Write(&everloop_image);
    usleep(40000);

  }
}
  
  void pattern2(matrix_hal::EverloopImage everloop_image,matrix_hal::Everloop everloop)
{

for (matrix_hal::LedValue &led : everloop_image.leds) {
    led.red = 0;
    // Set green to 100
    led.green = 100;
    led.blue = 0;
    led.white = 0;
}
    everloop.Write(&everloop_image);
    usleep(40000);
  
  

}


void pattern3(matrix_hal::EverloopImage everloop_image,matrix_hal::Everloop everloop)
{

for (matrix_hal::LedValue &led : everloop_image.leds) {
    led.red = 100;
    // Set green to 100
    led.green = 0;
    led.blue = 0;
    led.white = 0;
}
    everloop.Write(&everloop_image);
    usleep(40000);
  
  

}

void pattern4(matrix_hal::EverloopImage everloop_image,matrix_hal::Everloop everloop)
{

for (matrix_hal::LedValue &led : everloop_image.leds) {
    led.red = 50;
    // Set green to 100
    led.green = 50;
    led.blue = 0;
    led.white = 0;
}
    everloop.Write(&everloop_image);
    usleep(40000);
  
  

}

int main() {
  matrix_hal::MatrixIOBus bus;
  // Initialize bus and exit program if error occurs
  if (!bus.Init()) return false;

  int ledCount = bus.MatrixLeds();
  // Create EverloopImage object, with size of ledCount
  matrix_hal::EverloopImage everloop_image(ledCount);
  // Create Everloop object
  matrix_hal::Everloop everloop;
  // Set everloop to use MatrixIOBus bus
  everloop.Setup(&bus);

  initMqtt(ADDRESS,CLIENTID,TOPIC,QOS);

   while(1){
       //std::cout<<msg<<std::endl;
     if(msg==0){
       pattern0(everloop_image,everloop);
     }

     if(msg==1){
       pattern1(everloop_image,everloop);
     }
         if(msg==2){
       pattern2(everloop_image,everloop);
     }
          if(msg==3){
       pattern3(everloop_image,everloop);
     }
          if(msg==4){
       pattern4(everloop_image,everloop);
     }

   }


  return 0;
}
