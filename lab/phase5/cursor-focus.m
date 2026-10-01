/* Private Wine 10 cursor fix. No system files or other apps are changed. */
#import <Cocoa/Cocoa.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <mach-o/dyld.h>
#include <stdio.h>
#include <string.h>

static void (*originalUpdate)(id, SEL, BOOL);
static Ivar currentFlag;
static Class controllerClass;
static unsigned diagnostics;

static BOOL overWineClient(void) {
    if (![NSApp isActive]) return NO;
    NSPoint point = [NSEvent mouseLocation];
    NSInteger number = [NSWindow windowNumberAtPoint:point belowWindowWithWindowNumber:0];
    NSWindow *window = [NSApp windowWithWindowNumber:number];
    if (!window || ![NSStringFromClass([window class]) isEqualToString:@"WineWindow"])
        return NO;
    NSRect client = [window convertRectToScreen:[[window contentView] frame]];
    return NSPointInRect(point, client);
}

static void update(id self, SEL selector, BOOL force) {
    if (overWineClient()) {
        /* AppKit may have restored the arrow without notifying Wine. */
        *(BOOL *)((char *)(void *)self + ivar_getOffset(currentFlag)) = NO;
        force = YES;
    }
    originalUpdate(self, selector, force);
}

static void refresh(void) {
    id controller = ((id (*)(id, SEL))objc_msgSend)(controllerClass, @selector(sharedController));
    if (diagnostics++ < 4) {
        NSPoint pt = [NSEvent mouseLocation];
        NSInteger number = [NSWindow windowNumberAtPoint:pt belowWindowWithWindowNumber:0];
        fprintf(stderr,"DS cursor focus: active=%d window=%ld class=%s inside=%d\n",
                [NSApp isActive],(long)number, [NSStringFromClass([[NSApp windowWithWindowNumber:number] class]) UTF8String],overWineClient());
    }
    update(controller, @selector(updateCursor:), NO);
}

static void install(void) {
    if (originalUpdate) return;
    controllerClass = objc_getClass("WineApplicationController");
    if (!controllerClass) return;
    Method method = class_getInstanceMethod(controllerClass, @selector(updateCursor:));
    currentFlag = class_getInstanceVariable(controllerClass, "cursorIsCurrent");
    if (!method || !currentFlag || strcmp(ivar_getTypeEncoding(currentFlag), "c")) {
        fprintf(stderr, "DS cursor fix: incompatible Wine class; inactive\n");
        return;
    }
    originalUpdate = (void *)method_setImplementation(method, (IMP)update);
    [[NSNotificationCenter defaultCenter]
        addObserverForName:NSApplicationDidBecomeActiveNotification object:nil
        queue:[NSOperationQueue mainQueue] usingBlock:^(NSNotification *notification) {
            dispatch_async(dispatch_get_main_queue(), ^{
                refresh();
            });
        }];
    [NSTimer scheduledTimerWithTimeInterval:0.1 repeats:YES block:^(NSTimer *timer) {
        refresh();
    }];
    fprintf(stderr, "DS cursor fix: installed private Wine focus correction\n");
}

static void imageAdded(const struct mach_header *header, intptr_t slide) {
    dispatch_async(dispatch_get_main_queue(), ^{ install(); });
}

__attribute__((constructor)) static void start(void) {
    _dyld_register_func_for_add_image(imageAdded);
}
