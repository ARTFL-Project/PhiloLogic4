// $Id: level.h,v 2.11 2004/05/28 19:22:06 o Exp $
// philologic 2.8 -- TEI XML/SGML Full-text database engine
// Copyright (C) 2004 University of Chicago
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the Affero General Public License as published by
// Affero, Inc.; either version 1 of the License, or (at your option)
// any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// Affero General Public License for more details.
// 
// You should have received a copy of the Affero General Public License
// along with this program; if not, write to Affero, Inc.,
// 510 Third Street, Suite 225, San Francisco, CA 94107 USA.

#ifdef BATCH_H
  #error "level.h multiply included"
#else

  #define BATCH_H

#ifndef C_H
  #include "c.h"
#endif

#ifndef WORD_H
  #include "word.h"
#endif

#ifndef BLOCKMAP_H
  #include "blockmap.h"
#endif

#ifndef GMAP_H
  #include "gmap.h"
#endif

#define MAXBATCHES  10

#define BATCH_PROCESSED           0
#define BATCH_PROCESSED_LAST      1
#define BATCH_EMPTY               2
#define BATCH_PROCESSING_ERROR    4


typedef struct Batch *Batch, Batch_;

struct Batch
{
  N32      howmany;  /* number of words in the batch */
  N32      total;    /* total frequency of the words in the batch */
  N32      number;   /* "real" number of the batch, used in phrase searches */
  N32      malloced; /* currently malloc-ed word list */

  N32      not_op;   /* boolean 'NOT' operator; */

  Word     w_list;   /* list of Word objects */

  hitcmp*  hit_cmp;

  blockMap blockmap; /* Block Map */
  N32      blockmap_l;
  N32      blkmapctr; 

  Gmap     map; 
  Gmap     res;
  Gmap     stored;
};

#ifndef SEARCH_H
  #include "search.h"
#endif

void init_batchObject ( Batch b, N32 n );
Z32 process_input ( Search s, FILE *f );
Z32 create_batches ( Search s, FILE *f );
Z32 process_batch ( Search s, FILE *f, N32 bn );
void sort_batches ( Batch b, N32 n );
int batch_sort_function ( const void *v0, const void *v1 );
void rearrange_batches ( Search s );
int delete_batch(Batch b);

#endif /* #ifdef BATCH_H */











