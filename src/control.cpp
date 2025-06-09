#include <control.h>
#include <Adafruit_NeoPixel.h>


Adafruit_NeoPixel pixels(4, NEO_PIXEL_PIN, NEO_GRB + NEO_KHZ800);


void setupNeoPixels() {
    pixels.begin();
    pixels.clear();
    pixels.show();
}


void setNeoPixel(int id, int color_array[4][3]) {
    for (int i = 0; i < 4; i++) {
        pixels.setPixelColor(i, pixels.Color(color_array[i][0], color_array[i][1], color_array[i][2]));
    }
    pixels.show();
}



void setFanState(int id, bool state) {
    digitalWrite(FAN_PIN, state ? HIGH : LOW);
}