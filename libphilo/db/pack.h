#include "db.h"
#include "gdbm.h"
#include "../c.h"

#define PHILO_INDEX_CUTOFF 10
#define PHILO_BLOCK_FULL 1

struct hitbuffer {
  dbh *db;
  Z32 *dir;
  Z32 *blk;
  Z8 type;
  N64 freq;
  N64 offset;
  Z8 in_block;
  Z8 word[512];
  N64 dir_length;
  N64 dir_malloced;
  N64 blk_length;
  N64 blk_malloced;
};

typedef struct hitbuffer hitbuffer;

hitbuffer *new_hb(dbspec *dbs);
int delete_hb(hitbuffer *hb);
int hitbuffer_init(hitbuffer *hb, Z8 *word);
int hitbuffer_inc(hitbuffer *hb, Z32 *hit);
int hitbuffer_finish(hitbuffer *hb);
