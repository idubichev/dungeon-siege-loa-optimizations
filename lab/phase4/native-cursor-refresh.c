/* Convert the game's immutable cursor images to native Win32 cursors.
 * Called only by the isolated software-cursor replacement. */
typedef unsigned int u32;
typedef unsigned short u16;
typedef void *Handle;
#define WINAPI __attribute__((stdcall))
typedef Handle (WINAPI *GetModule)(const char *);
typedef Handle (WINAPI *GetProc)(Handle,const char *);
typedef struct { int width,height; u32 reserved; const u32 *pixels; } Image;
typedef struct {
    u32 size; int width,height; u16 planes,bpp;
    u32 compression,image_size; int xppm,yppm; u32 colors,important;
    u32 v5[21];
} BitmapHeader;
typedef struct { int icon; u32 x,y; Handle mask,color; } IconInfo;
typedef Handle (WINAPI *CreateDIB)(Handle,const BitmapHeader*,u32,void**,Handle,u32);
typedef Handle (WINAPI *CreateBitmap)(int,int,u32,u32,const void*);
typedef Handle (WINAPI *CreateIcon)(const IconInfo*);
typedef int (WINAPI *DeleteObject)(Handle);
typedef Handle (WINAPI *SetCursor)(Handle);
typedef struct { const Image *image; const u32 *pixels; int w,h,x,y; Handle handle; } Entry;
typedef struct {
    Handle current;
    u32 count,hits,fallbacks;
    CreateDIB create_dib;
    CreateBitmap create_bitmap;
    CreateIcon create_icon;
    DeleteObject delete_object;
    SetCursor set_cursor;
    u32 reserved;
    Entry entries[64];
    unsigned char zero_mask[8192];
} State;

Handle WINAPI build_cursor(const Image *image,int x,int y,State *s,GetModule module,GetProc proc) {
    if (!s->create_dib) {
        Handle gdi=module("gdi32.dll"), user=module("user32.dll");
        if (!gdi || !user) goto fallback;
        s->create_bitmap=(CreateBitmap)proc(gdi,"CreateBitmap");
        s->create_icon=(CreateIcon)proc(user,"CreateIconIndirect");
        s->delete_object=(DeleteObject)proc(gdi,"DeleteObject");
        s->set_cursor=(SetCursor)proc(user,"SetCursor");
        CreateDIB create_dib=(CreateDIB)proc(gdi,"CreateDIBSection");
        if (!create_dib || !s->create_bitmap || !s->create_icon || !s->delete_object || !s->set_cursor) goto fallback;
        s->create_dib=create_dib;
    }
    if (!image || !image->pixels || image->width<1 || image->width>256 || image->height<1 || image->height>256 || x<0 || y<0 || x>=image->width || y>=image->height) goto fallback;
    for (u32 i=0;i<s->count;i++) {
        Entry *e=&s->entries[i];
        if (e->image==image && e->pixels==image->pixels && e->w==image->width && e->h==image->height && e->x==x && e->y==y) {
            s->current=e->handle;
            s->hits++;
            s->set_cursor(0); /* Refresh the Mac cursor after native app focus changes. */
            s->set_cursor(e->handle);
            return e->handle;
        }
    }
    if (s->count>=64) goto fallback;
    BitmapHeader h;
    h.size=124; h.width=image->width; h.height=-image->height;
    h.planes=1; h.bpp=32; h.compression=3; h.image_size=0;
    h.xppm=0;h.yppm=0;h.colors=0;h.important=0;
    for (int i=0;i<21;i++) h.v5[i]=0;
    h.v5[0]=0x00ff0000;h.v5[1]=0x0000ff00;h.v5[2]=0x000000ff;
    h.v5[3]=0xff000000;h.v5[4]=0x73524742;
    u32 *bits=0;
    Handle color=s->create_dib(0,&h,0,(void**)&bits,0,0);
    if (!color || !bits) { if(color)s->delete_object(color); goto fallback; }
    for (int i=0;i<image->width*image->height;i++) {
        u32 p=image->pixels[i],a=p>>24;
        u32 b=(p&255)*a+128,g=((p>>8)&255)*a+128,r=((p>>16)&255)*a+128;
        b=(b+(b>>8))>>8;g=(g+(g>>8))>>8;r=(r+(r>>8))>>8;
        /* This pinned Wine Mac driver displays R/B reversed for native cursors. */
        bits[i]=(a<<24)|(b<<16)|(g<<8)|r;
    }
    Handle mask=s->create_bitmap(image->width,image->height,1,1,s->zero_mask);
    if (!mask) { s->delete_object(color); goto fallback; }
    IconInfo info;
    info.icon=0;info.x=x;info.y=y;info.mask=mask;info.color=color;
    Handle cursor=s->create_icon(&info);
    s->delete_object(mask);s->delete_object(color);
    if (!cursor) goto fallback;
    Entry *e=&s->entries[s->count];
    e->image=image;e->pixels=image->pixels;e->w=image->width;e->h=image->height;
    e->x=x;e->y=y;e->handle=cursor;
    s->count++;
    s->current=cursor;
    s->set_cursor(cursor);
    return cursor;
fallback:
    s->fallbacks++;
    s->current=0;
    if (s->set_cursor) s->set_cursor(0);
    return 0;
}
