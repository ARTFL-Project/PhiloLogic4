// $Id: blockmap.c,v 2.11 2004/05/28 19:22:06 o Exp $
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

#include <stdlib.h>
#include <string.h>
#include "blockmap.h"

#ifndef SEARCH_H
  #include "search.h"
#endif

void init_blockMapObject ( blockMap b, Word w, Z32 bn, Z32 n)
{
  b->w  = w; 
  b->n  = n; 
  b->bn = bn;
}

Z32 load_blockmap ( blockMap blockmap, Word w, Search s, Z32 bn )
{

  N32 n; /* number of blocks/words */
  N32 c = 0; 

  n = w->type ? w->blkcount : w->freq; 

  s_logf ( s->debug, L_INFO, "word of type %d;", w->type ); 
  s_logf ( s->debug, L_INFO, "%d virtual blocks;", n ); 

  while ( c < n )
    {
      init_blockMapObject ( blockmap + c, w, bn, c );
      c++;
    }

  return n; 
}

int blockmap_sort_func ( const void *v1, const void *v2 )
{
  static Search s = NULL; 

  blockMap b1;
  blockMap b2;

  Z32    bn;

  Z32    *x;
  Z32    *y; 

  Z32     i; 

  if ( v1 == NULL )
    {
      s = (Search)v2;
    }
  else
    {
      if ( !s )
	{
	  s_log ( s->debug, L_ERROR, NULL, "uninitialized sort function used!" );
	  exit (1);
	}

      b1 = (blockMap)v1; 
      b2 = (blockMap)v2; 
      /*
      fprintf ( stderr, "attempting to compare blockmap objects\n" ); 
      */

      bn = s->bn;
      /*
      s_logf ( s->debug, L_INFO, "this is search level %d;\n", bn ); 
       */

      if ( b1->w->n_cached && ( b1->w->blk_cached == b1->n ) )
	{
	  x = (Z32 *)b1->w->cached; 
	}
      else
	x = (Z32 *)&b1->w->dir->gm_h[(b1->w->dir->gm_f)*(b1->n)]; 

      if ( b2->w->n_cached && ( b2->w->blk_cached == b2->n ) )
	{
	  y = (Z32 *)b2->w->cached; 
	}
      else
	y = (Z32 *)&b2->w->dir->gm_h[(b2->w->dir->gm_f)*(b2->n)];

      /*
      x += b1->n; 
      y += b2->n; 
      s_logf ( s->debug, L_INFO, "block object 1: b1->n = %d", b1->n );
      s_logf ( s->debug, L_INFO, "block object 2: b2->n = %d", b2->n );
      */
      
      /*return s->hit_def->levels[bn].h2h_cmp_func ( x, y, s->hit_def, bn );*/
      
      /* temporary hack: */

      /* and why is it temporary? -- because we are using the specific
	 knowlegde of how our hits are structured; of which this level
	 of the program should not have any! So our search plugin must
	 include a special function for hit-to-hit comparisons that we
	 could use here; Note on philologic hits: while using the
	 "phrase check" function for this would technically work, for
	 purposes of simple "more" or "less" comparison it would be
	 cheaper to use a function that only compares doc. numbers and
	 byte offsets!
      */
         

      for ( i = 0; i < INDEX_DEF_WORD; i++ )
	if ( x[i] < y[i] )
	  return -1;
	else if ( x[i] > y[i] )
	  return 1; 

      return 0; 

      /* end of temporary hack. */
    }

  return 0; 
}

Z32 blockmap_resort ( Search s, Z32 bn )
{
  blockMap b = s->batches[bn].blockmap;

  N32    b_l = s->batches[bn].blockmap_l; 
  N32    b_c = s->batches[bn].blkmapctr;  

  Z32    res = 0; 
  Z32    howmany_items = 0; 

  int    j; 

  static blockMap_ b_cache[2];

  if ( b_c == b_l - 1 )
    return 0; 

  res = blockmap_sort_func ( (const void *)(b+b_c), (const void *)(b+b_c+1) );

  if ( res < 0 )
    /* blockmap is ok! */
    return 0; 
  else
    {
      memcpy ( (void *)b_cache, (const void *)(b+b_c), sizeof (blockMap_) );

      while ( ( b_c < b_l-1) && ( blockmap_sort_func ( (const void *)(b+s->batches[bn].blkmapctr), (const void *)(b+b_c+1) ) > 0 ) )
	{
	  b_c++; 
	  howmany_items++; 
	}

      memmove ( (void *)(b+(s->batches[bn].blkmapctr)), (const void*)(b+s->batches[bn].blkmapctr+1), (size_t)sizeof (blockMap_) * howmany_items ); 

      memcpy ( (void *)(b+b_c), (const void *)b_cache, (size_t)sizeof(blockMap_)); 
    }
      
  return howmany_items; 
}

void blockmap_sort ( Search s, Z32 bn )
{
  blockMap b = s->batches[bn].blockmap;
  N32    b_l = s->batches[bn].blockmap_l; 
  N32    b_c = s->batches[bn].blkmapctr;  

  s_logf (s->debug, L_INFO, "sorting blockmap; %d objects", b_l);
  s_logf (s->debug, L_INFO, "sorting blockmap; counter=%d", b_c);

   
  blockmap_sort_func ( NULL, (const void *)s ); 
  qsort ( b + b_c, b_l - b_c, sizeof (blockMap_), blockmap_sort_func ); 
}

Z32 build_blockMap ( Search s, Z32 bn )
{
  Z32 i; 
  Z32 c = 0; 

  Batch b = s->batches + bn;

  b->blockmap = 
    (blockMap) malloc ( (b->blockmap_l + 1) * sizeof (blockMap_)); 

  s_logf (s->debug, L_INFO, "malloc-ed %d blockMap_ objects;", b->blockmap_l + 1);

  if ( ! b->blockmap )
    return BLOCKMAP_MALLOC_ERROR;

  for ( i = 0; i < b->howmany; i++ )
    c += load_blockmap ( b->blockmap + c, b->w_list + i, s, bn ); 

  if ( c != b->blockmap_l )
    return BLOCKMAP_BUILD_ERROR; 

  s_logf ( s->debug, L_INFO, "loaded blockmap with %d blocks total", c );

  if ( b->howmany > 1 )
    {
      s_log ( s->debug, L_INFO, NULL, "sorting blockmap..." );
      blockmap_sort ( s, bn );
      s_log ( s->debug, L_INFO, NULL, "done." );
    }

  return BLOCKMAP_BUILT;
}












