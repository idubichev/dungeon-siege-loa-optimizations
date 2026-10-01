#import <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc,char **argv) {
 CGEventRef current=CGEventCreate(NULL);CGPoint a=CGEventGetLocation(current);CFRelease(current);
 double dx=atof(argv[1]),dy=atof(argv[2]);CGPoint b=CGPointMake(a.x+dx,a.y+dy);
 CGEventRef e=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,b,kCGMouseButtonLeft);
 CGEventSetIntegerValueField(e,kCGMouseEventDeltaX,(int64_t)dx);CGEventSetIntegerValueField(e,kCGMouseEventDeltaY,(int64_t)dy);
 CGEventPost(kCGHIDEventTap,e);CFRelease(e);usleep(300000);
 current=CGEventCreate(NULL);b=CGEventGetLocation(current);CFRelease(current);
 printf("{\"before\":[%.1f,%.1f],\"after\":[%.1f,%.1f]}\n",a.x,a.y,b.x,b.y);
 return 0;
}
