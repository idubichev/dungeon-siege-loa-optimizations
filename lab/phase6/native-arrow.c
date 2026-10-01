/* Native arrow with absolute pointing; hide it during relative camera movement. */
typedef unsigned U;
typedef void *H;
#define W __attribute__((stdcall))
typedef H (W *Module)(const char *);
typedef H (W *Proc)(H,const char *);
typedef struct { U size,flags; H handle; int x,y; } CursorInfo;
typedef struct {
    H current; U count,hits,fallbacks;
    H (W *load)(H,const char *);
    H (W *set)(H);
    int (W *info)(CursorInfo *);
    int (W *show)(int);
    const unsigned char *window;
    H arrow;
} State;
H W build_cursor(const void *image,int x,int y,State *s,Module module,Proc proc) {
    if (!s->arrow) {
        H user=module("user32.dll");
        s->load=(void *)proc(user,"LoadCursorA");
        s->set=(void *)proc(user,"SetCursor");
        s->info=(void *)proc(user,"GetCursorInfo");
        s->show=(void *)proc(user,"ShowCursor");
        if (!s->load || !s->set || !s->info || !s->show) goto fallback;
        s->arrow=s->load(0,(const char *)32512);
        if (!s->arrow) goto fallback;
        s->count=1;
    }
    if (s->window && (*(const U *)(s->window+0x48)&0x10000000)) {
        s->current=0;
        s->set(0);
    } else {
        CursorInfo info;info.size=sizeof(info);
        if (s->info(&info) && !(info.flags&1)) {
            int count=s->show(1);
            if (count>0) s->show(0);
            for (U i=0;i<31 && count<0;i++) count=s->show(1);
        }
        s->current=s->arrow;
        s->set(s->current);
    }
    s->hits++;
    return s->arrow;
fallback:
    s->fallbacks++;
    return 0;
}
