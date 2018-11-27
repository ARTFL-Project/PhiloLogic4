// $Id: level.c,v 2.11 2004/05/28 19:22:06 o Exp $
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

#include <stdio.h>
#include <string.h>
#include "level.h"

void init_batchObject ( Batch b, N32 n )
{
  /* batch object initialization: */

  b->number  =  n; 
  b->howmany =  0; 
  b->total   =  0;

  b->w_list  = (Word) malloc ( sizeof(Word_) * INITWORDS );
  b->malloced = INITWORDS; 
  b->not_op = 0;
  b->blockmap_l = 0;
  b->blkmapctr  = 0;
  b->blockmap = NULL; 

  b->map      = NULL;
  b->res      = NULL;
  b->stored   = NULL;
}

Z32 process_input ( Search s, FILE *f ) 
{
  Z32 ret; 
  s_log ( s->debug, L_INFO, NULL, "entering input processing unit..." ); 
  s_log ( s->debug, L_INFO, NULL, "attempting to create batches:" ); 
  ret = create_batches ( s, f ); 
  if ( ret ) {
    if ( ret > 0 ) {
      s_log ( s->debug, L_INFO, NULL, "one of the search levels contained no words." ); 
      return 2; 
    }
    else {
      s_log ( s->debug, L_ERROR, NULL, "Could not create batches." ); 
      return -1; 
    }
  }
  else {
    s_logf ( s->debug, L_INFO, "%d batches created", s->depth ); 
    s->batches->map = s->map;
    return 0; 
  }
}

Z32 create_batches ( Search s, FILE *f )
{
  Batch b = s->batches;

  N32   b_counter = 0;
  Z32   b_status;
  Z32   i = 0;

  /* we initialize the 1st batch: */
  
  s_log ( s->debug, L_INFO, NULL, "initializing 1st batch..." );
  init_batchObject ( b, b_counter ); 
  s_log ( s->debug, L_INFO, NULL, "done." );

  while ( (b_status = process_batch ( s, f, b_counter++ )) != BATCH_PROCESSING_ERROR ) {
    s_logf ( s->debug, L_INFO, "process_batch returned %d", b_status );
    /* exit status BATCH_EMPTY means that there's nothing to search for; */
    /* unless this is "BOOLEAN NOT" level -- then it's ok. */
    if ( b_status & BATCH_EMPTY ) {
      if ( !s->batches[b_counter-1].not_op  ) {
		return BATCH_EMPTY;
      }
      b_counter--;
      for ( i = b_counter; i < s->depth - 1; i++ ) {
		s->batches[i].not_op = s->batches[i+1].not_op;
      }
    }
    if ( b_status & BATCH_PROCESSED_LAST ) {
      break; 
    }
    s_log ( s->debug, L_INFO, NULL, "initializing next batch..." );
    init_batchObject ( b + b_counter, b_counter );
    s_log ( s->debug, L_INFO, NULL, "done." );
  }
  s_logf ( s->debug, L_INFO, "last process_batch returned %d", b_status );
  if ( b_status == BATCH_PROCESSING_ERROR ) {
    return BATCH_PROCESSING_ERROR; 
  }

  /* we now sort the "batches" to process the less frequent 
     words during the first passes, and the "boolean not" 
     batches when all "real" batches are processed. */

  s_log ( s->debug, L_INFO, NULL, "attempting to sort batches;" );
  sort_batches ( b, b_counter ); 
  s_log ( s->debug, L_INFO, NULL, "(done)" );

  /* hack: */

  for ( i = 0; i < b_counter; i++ ) {
    s->hit_def->levels[i].n_real = b[i].number;
  }

  s->hit_def->depth   = s->depth; 
  s->hit_def->depth_r = s->depth_r; 

  /* a hack indeed; :( */

  s->depth = b_counter; 
  return BATCH_PROCESSED; 
}

Z32 process_batch ( Search s, FILE *f, N32 bn ) 
/*reads words from input, line by line, and adds them to the word vector for the current batch object.*/
{
  Batch b = s->batches + bn; 
  N32   n_blocks = 0; 

  Z8  word[W_LENGTH_MAX]; 
  Z8  lmsg[W_LENGTH_MAX];

  N32  n; 
  N32  ret = BATCH_PROCESSED; 

  while ( fgets(  (char *)word, W_LENGTH_MAX, f)  && strcmp ( (char *)word, "\n") ) {
    word[strlen( (char *)word)-1] = '\000'; /* chop */
    s_logf ( s->debug, L_INFO, "read word %s", word ); 
    if ( b->howmany == b->malloced ) {
      b->w_list = (Word) realloc ( b->w_list, sizeof(Word_) * ( b->malloced + INITWORDS ) ); 
      b->malloced += INITWORDS; 
    }
    if ( (n = init_wordObject (s, word, b->w_list + b->howmany, &n_blocks )) ) { //we do an initial lookup to get word frequency.
      s_logf ( s->debug, L_INFO, "(word object initialized with %d occurencees)", n ); 
      b->total += n;
      b->howmany++; 
      b->blockmap_l += n_blocks;
    }
  }

  if ( !b->howmany ) {
    ret |= BATCH_EMPTY;
  }
  if ( s->debug ) {
    sprintf ((char *)lmsg, "read %d words, %d/%d occurences/blocks total", b->howmany, b->total, b->blockmap_l); 
    s_log ( s->debug, L_INFO, NULL, lmsg );
    s_log ( s->debug, L_INFO, NULL, "attempting to build blockmap..." );
  }
  if ( build_blockMap ( s, bn ) ) {
    s_log ( s->debug, L_ERROR, NULL, "error building blockmap" );
    sprintf ( s->errstr, "error building blockmap (level %d).\n", bn );
    return BATCH_PROCESSING_ERROR;
  }
  s_log ( s->debug, L_INFO, NULL, "done." );
  if ( strcmp (word, "\n") ) {
    ret |= BATCH_PROCESSED_LAST; 
  }
  return ret;
}

void sort_batches ( Batch b, N32 n )
{
  qsort ( b, n, sizeof (Batch_), batch_sort_function ); 
}

int batch_sort_function ( const void *v0, const void *v1 )
{
  const struct Batch *b0 = v0;
  const struct Batch *b1 = v1;
  N32 t0 = b0->total; 
  N32 t1 = b1->total; 

  if (( ! b0->not_op ) && ( ! b1->not_op )) 
    return t0 < t1 ? -1 : t0 > t1 ? 1 : 0; 

  if ( b0->not_op && b1->not_op ) 
    return t0 > t1 ? -1 : t0 < t1 ? 1 : 0;

  if ( b0->not_op )
    return 1; 

  return -1; 

}

void rearrange_batches ( Search s ) // positions NOT_OP terms correctly.  tricky.  where is this called from?
{
  Z32 i = 0; 
  Batch b; 
  if ( s->batches->not_op ) {
    s_log ( s->debug, L_INFO, NULL, "attempting to rearrange batches;" );
    while ( s->batches[i].not_op ) {
      s_logf ( s->debug, L_INFO, "batch number %d has NOT_OP set;", i ); 
      i++; 
    }
    b = (Batch) malloc ( sizeof (Batch_) ); 
    /*(void)memcpy ((void *)b, (const void *)(s->batches+i), sizeof (Batch_));*/
    memcpy (b, &(s->batches[i]), sizeof (Batch_)); 
    memmove (&(s->batches[1]), s->batches, sizeof (Batch_) * i); 
    memcpy (s->batches, b, sizeof (Batch_)); 
    /*s->batches[i] = *b;*/
    for ( i = 0; i < s->depth; i++ ) {
      s->hit_def->levels[i].n_real = s->batches[i].number;
      s_logf ( s->debug, L_INFO, "batch: word number %d", s->batches[i].number );
    }
  }
  else {
    s_log ( s->debug, L_INFO, NULL, "no rearrangement necessary" );
  }
}

int delete_batch(Batch b) {
  free(b->blockmap);
  free(b->w_list);
  free(b);
  return 0;
}





