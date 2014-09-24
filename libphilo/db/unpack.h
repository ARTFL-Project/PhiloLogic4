#ifndef _INC_UNPACK_H
#define _INC_UNPACK_H

#include "db.h"
#include "bitsvector.h"
#include <stdint.h>

int word_lookup(dbh *db, Z8 *keyword);

Z32 *hit_lookup(dbh *db, Z8 *keyword, N32 *type_num, N32 *freq, N32 *blkcount, N64 *offset);
Z32 *unpack(dbh *db, bitsvector *v, N32 count);
Z32 *hit_gethits(dbh *db, N32 type, Z32 *first, N64 offset, N32 *blockcount);
#endif
