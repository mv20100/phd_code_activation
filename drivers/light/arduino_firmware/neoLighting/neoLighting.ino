#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#define PIN 6
#define NUMPIXELS 12
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
// how much serial data we expect before a newline
const unsigned int MAX_INPUT = 50;
int red=0;
int green=0;
int blue=0;

void setup() {
  // Initialize all pixels to 'off'
  pixels.begin();
  pixels.show();
  Serial.begin(9600);
}

void loop() {
  while (Serial.available () > 0)
    processIncomingByte (Serial.read ());
}

void processIncomingByte (const byte inByte)
  {
  static char input_line [MAX_INPUT];
  static unsigned int input_pos = 0;
  switch (inByte)
    {
    case '\n':   // end of text
      input_line [input_pos] = 0;  // terminating null byte
      // terminator reached! process input_line here ...
      process_data (input_line);
      input_pos = 0;          // reset buffer for next time
      break;
    case '\r':   // discard carriage return
      break;
    default:
      // keep adding if not full ... allow for terminating null byte
      if (input_pos < (MAX_INPUT - 1))
        input_line [input_pos++] = inByte;
      break;
    }  // end of switch
  } // end of processIncomingByte  

void process_data(char* inputString){
  char* command = strtok(inputString, ";");
  while (command != 0)
  {
    // Split the command in two values
    char* separator = strchr(command, ':');
    if (separator != 0)
    {
        // Actually split the string in 2: replace ':' with 0
        *separator = 0;
        ++separator;
        processCommand(command,separator);
        // Do something with servoId and position
    }
    else{
      processCommand(command,"");
    }
    // Find the next command in input string
    command = strtok(0, ";");
  }
}

void processCommand(char* command,char* param){
  char line[20];
  sprintf(line,"Command: %s, Param: %s",command,param);
  //Serial.println(line);
  switch (command[0]){
    case 'w':
      red = atoi(param);
      green = atoi(param);
      blue = atoi(param);
      setAllPixels();
      break;
    case 'r':
      red = atoi(param);
      setAllPixels();
      break;
    case 'g':
      green = atoi(param);
      setAllPixels();
      break;
    case 'b':
      blue = atoi(param);
      setAllPixels();
      break;
  }
}

void setAllPixels(){
  for(int i=0;i<NUMPIXELS;i++){
    // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
    pixels.setPixelColor(i, pixels.Color(red,green,blue)); // Moderately bright green color.
    pixels.show(); // This sends the updated pixel color to the hardware.
  }
}
//  if (inputString == "on"){
//    Serial.println("ON");
//    setAllPixels(255,0,0);
//  }
//  if (inputString == "off"){
//    Serial.println("OFF");
//    setAllPixels(0,0,0);
//  }

