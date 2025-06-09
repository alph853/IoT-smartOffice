#ifndef CONTROL_H
#define CONTROL_H

#include <config.h>


void setupNeoPixels();
void setNeoPixel(int id, int color_array[4][3]);
void setFanState(int id, bool state);


#endif
