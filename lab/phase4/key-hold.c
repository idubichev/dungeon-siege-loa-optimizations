#include <ApplicationServices/ApplicationServices.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 CGKeyCode key=(CGKeyCode)strtoul(argv[1],0,10);
 CGEventRef down=CGEventCreateKeyboardEvent(0,key,true),up=CGEventCreateKeyboardEvent(0,key,false);
 CGEventPost(kCGHIDEventTap,down);usleep(strtoul(argv[2],0,10)*1000);
 CGEventPost(kCGHIDEventTap,up);CFRelease(down);CFRelease(up);return 0;
}
