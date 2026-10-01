#import <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
int main(int argc,char **argv) {
 if(argc==3) {CGEventRef e=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,CGPointMake(atof(argv[1]),atof(argv[2])),kCGMouseButtonLeft);CGEventPost(kCGHIDEventTap,e);CFRelease(e);}
 CGEventRef e=CGEventCreate(NULL);CGPoint q=CGEventGetLocation(e);printf("%.1f %.1f\n",q.x,q.y);CFRelease(e);return 0;
}
