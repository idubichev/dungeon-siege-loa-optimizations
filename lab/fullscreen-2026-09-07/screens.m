#import <AppKit/AppKit.h>
int main(){ @autoreleasepool { for(NSScreen *s in [NSScreen screens]) NSLog(@"frame=%@ visible=%@ scale=%g",NSStringFromRect(s.frame),NSStringFromRect(s.visibleFrame),s.backingScaleFactor); } }
