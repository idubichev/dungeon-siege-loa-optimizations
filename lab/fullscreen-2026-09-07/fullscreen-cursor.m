/* dgVoodoo draws the scaled Win32 pointer. Suppress its unscaled AppKit duplicate only inside the fullscreen game. */
#import <Cocoa/Cocoa.h>
#import <objc/runtime.h>
static void (*originalSet)(id,SEL);
static NSCursor *blank;
static BOOL inGame(void) {
 if (![NSApp isActive]) return NO;
 NSWindow *w=[NSApp keyWindow];
 if (!w || ![[w title] isEqualToString:@"Dungeon Siege"]) return NO;
 NSRect a=[w frame],b=[[w screen] frame];
 return fabs(a.size.width-b.size.width)<2 && fabs(a.size.height-b.size.height)<2;
}
static void setCursor(id self,SEL sel) {originalSet(inGame()?blank:self,sel);}
__attribute__((constructor)) static void install(void) {
 dispatch_async(dispatch_get_main_queue(), ^{
  blank=[[NSCursor alloc] initWithImage:[[NSImage alloc] initWithSize:NSMakeSize(2,2)] hotSpot:NSZeroPoint];
  Method m=class_getInstanceMethod([NSCursor class],@selector(set));
  originalSet=(void *)method_setImplementation(m,(IMP)setCursor);
  for (NSString *name in @[NSApplicationDidBecomeActiveNotification,NSApplicationDidResignActiveNotification,NSWindowDidBecomeKeyNotification]) {
   [[NSNotificationCenter defaultCenter] addObserverForName:name object:nil queue:[NSOperationQueue mainQueue] usingBlock:^(NSNotification *n){ [[NSCursor arrowCursor] set]; }];
  }
  fprintf(stderr,"DS fullscreen cursor presentation fix installed\n");
 });
}
