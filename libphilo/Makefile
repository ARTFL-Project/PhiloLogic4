# $Id: Makefile.in,v 2.11 2004/05/28 19:22:06 o Exp $
LDFLAGS=
CFLAGS= -O3
CPPFLAGS=
LDFLAGS=
PH_CFLAGS= -I./unpack -D_REENTRANT -fomit-frame-pointer -finline-functions
CC= gcc
PH_BUILDENV =
PH_LDSEARCHFLAGS =

all: 	search5 db/pack5

db/pack5: db/pack.c db/pack.h db/db.c db/db.h
	$(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -o db/pack5 db/pack.c db/db.c -lgdbm

search5: search4.c search.o retreive.o gmap.o word.o blockmap.o level.o out.o plugin/libindex.a db/db.o db/bitsvector.o db/unpack.o
	$(PH_BUILDENV) $(CC) $(CFLAGS) $(CPPFLAGS) $(PH_CFLAGS) $(LDFLAGS) $(PH_LDSEARCHFLAGS) search4.c search.o retreive.o gmap.o word.o blockmap.o level.o out.o db/db.o db/bitsvector.o db/unpack.o plugin/libindex.a -lgdbm -o search5

libphilo.dylib: search.o word.o retreive.o level.o gmap.o blockmap.o log.h out.o plugin/libindex.a db/db.o db/bitsvector.o db/unpack.o
	$(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -dynamiclib -std=gnu99 search.o word.o retreive.o level.o gmap.o blockmap.o out.o plugin/libindex.a db/db.o db/bitsvector.o db/unpack.o -lgdbm -o libphilo.dylib

db/db.o:  db/db.c db/db.h db/bitsvector.c db/bitsvector.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o db/db.o -c db/db.c

db/bitsvector.o: db/bitsvector.c db/bitsvector.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o db/bitsvector.o -c db/bitsvector.c

db/unpack.o: db/unpack.c db/unpack.c db/bitsvector.c db/bitsvector.h db/db.c db/db.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o db/unpack.o -c db/unpack.c

plugin/libindex.a: plugin/hitdef.o plugin/hitcmp_sent.o plugin/hitcmp_cooc.o plugin/hitcmp_phrase.o plugin/hitcmp_proxy.o plugin/hitout.o plugin/hitman.o plugin/hitcrp.o plugin/method.o plugin/plugin.o
	ar ru $@ plugin/hitdef.o plugin/hitcmp_cooc.o plugin/hitcmp_phrase.o plugin/hitcmp_proxy.o plugin/hitout.o plugin/hitman.o plugin/hitcrp.o plugin/method.o plugin/plugin.o plugin/hitcmp_sent.o
	ranlib $@

plugin/method.o:	plugin/method.c plugin/method.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/method.o -c plugin/method.c

plugin/plugin.o:	plugin/plugin.c plugin/plugin.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/plugin.o -c plugin/plugin.c

plugin/hitdef.o: 	plugin/hitdef.c plugin/hitcon.h plugin/hitcmp.h plugin/hitdef.h plugin/hitman.h plugin/hitout.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitdef.o -c plugin/hitdef.c

plugin/hitcmp_cooc.o: 	plugin/hitcmp_cooc.c plugin/hitcon.h plugin/hitcmp.h plugin/hitdef.h plugin/hitman.h plugin/hitout.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitcmp_cooc.o -c plugin/hitcmp_cooc.c

plugin/hitcmp_phrase.o: 	plugin/hitcmp_phrase.c plugin/hitcon.h plugin/hitcmp.h plugin/hitdef.h plugin/hitman.h plugin/hitout.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitcmp_phrase.o -c plugin/hitcmp_phrase.c

plugin/hitcmp_proxy.o: 	plugin/hitcmp_proxy.c plugin/hitcon.h plugin/hitcmp.h plugin/hitdef.h plugin/hitman.h plugin/hitout.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitcmp_proxy.o -c plugin/hitcmp_proxy.c

plugin/hitcmp_sent.o: plugin/hitcmp_sent.c plugin/hitcmp_sent.h plugin/hitcon.h plugin/hitcmp.h plugin/hitdef.h plugin/hitman.h plugin/hitout.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitcmp_sent.o -c plugin/hitcmp_sent.c

plugin/hitout.o: 	plugin/hitout.c plugin/hitcon.h plugin/hitout.h plugin/hitdef.h plugin/hitman.h plugin/hitcmp.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitout.o -c plugin/hitout.c

plugin/hitman.o: 	plugin/hitman.c plugin/hitcon.h plugin/hitman.h plugin/hitdef.h plugin/hitcmp.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitman.o -c plugin/hitman.c

plugin/hitcrp.o: 	plugin/hitcrp.c plugin/hitcon.h plugin/hitdef.h plugin/hitcmp.h
	$(CC) $(CFLAGS) $(CPPFLAGS) -o plugin/hitcrp.o -c plugin/hitcrp.c

gmap.o:		gmap.h gmap.c c.h

word.o:		word.h word.c c.h

level.o:	level.h blockmap.h gmap.h word.h level.c c.h

blockmap.o:	blockmap.h blockmap.c level.h word.h search.h c.h

search.o:	search.c blockmap.h blockmap.c level.h word.h search.h c.h

out.o:		out.h out.c

log.o:		log.h log.c

install:	all
	/usr/bin/install -c search5 ${exec_prefix}/bin
	/usr/bin/install -c db/pack5 ${exec_prefix}/bin
clean:
	rm -f *.o *~ search5 db/pack5
	(cd plugin; make clean)
	(cd db; make clean)
