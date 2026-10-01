/* Use Wine's system arrow instead of reading back GPU pixels for a cursor. */
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
} State;

H W build_cursor(const void *image,int x,int y,State *s,Module module,Proc proc) {
    if (!s->current) {
        H user=module("user32.dll");
        s->load=(void *)proc(user,"LoadCursorA");
        s->set=(void *)proc(user,"SetCursor");
        s->info=(void *)proc(user,"GetCursorInfo");
        s->show=(void *)proc(user,"ShowCursor");
        if (!s->load || !s->set || !s->info || !s->show) goto fallback;
        s->current=s->load(0,(const char *)32512);
        if (!s->current) goto fallback;
        s->count=1;
    }
    CursorInfo info;info.size=sizeof(info);
    if (s->info(&info) && !(info.flags&1)) {
        int count=s->show(1);
        if (count>0) s->show(0);
        for (U i=0;i<31 && count<0;i++) count=s->show(1);
    }
    s->set(s->current);
    s->hits++;
    return s->current;
fallback:
    s->fallbacks++;
    return 0;
}
