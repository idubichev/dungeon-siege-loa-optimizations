#import <Cocoa/Cocoa.h>
#import <CoreGraphics/CoreGraphics.h>
int main(){ @autoreleasepool {
 NSArray *windows=(__bridge_transfer NSArray*)CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly|kCGWindowListExcludeDesktopElements,kCGNullWindowID);
 for(NSDictionary *w in windows){ NSString *n=w[(id)kCGWindowOwnerName]; if([n rangeOfString:@"wine" options:NSCaseInsensitiveSearch].location!=NSNotFound || [n rangeOfString:@"siege" options:NSCaseInsensitiveSearch].location!=NSNotFound || [n rangeOfString:@"DSLOA" options:NSCaseInsensitiveSearch].location!=NSNotFound) { NSData *j=[NSJSONSerialization dataWithJSONObject:w options:0 error:nil]; puts([[NSString alloc] initWithData:j encoding:NSUTF8StringEncoding].UTF8String); } }
} }
