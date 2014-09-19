// $Id: retreive.c,v 2.11 2004/05/28 19:22:06 o Exp $
// philologic 2.8 -- TEI XML/SGML Full-text database engine
// Copyright (C) 2004 University of Chicago
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the Affero General Public License as published by
// Affero, Inc.; either version 1 of the License, or\ (at your option)
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
#include "string.h"
#include "retreive.h"
#include "db/unpack.h"

N32 retreive_hits ( Search s, N level, Gmap map, Gmap res )
{
  Batch b = s->batches + level; 
  Word w = b->blockmap[b->blkmapctr].w; 
  N32  n = b->blockmap[b->blkmapctr].n; 
  Z32  status; 

  s_logf ( s->debug, L_INFO, "retreive: level %d,", level ); 
  s_logf ( s->debug, L_INFO, "retreive: blockmap counter %d,", b->blkmapctr ); 
  s_logf ( s->debug, L_INFO, "retreive: dir. number in the block object %d;", n ); 

  status = process_block_unit ( s, level, w, n, map, res );

  s_logf ( s->debug, L_INFO, "process_block_unit returned %d;", status );

  if ( status & RETR_BUMMER ) {
    return SEARCH_BUMMER_OCCURED;
  }
  /* smart, although the blockmap manipulations below should 
     probably be done in search.c: */
  if ( status & RETR_BLK_CLEAN ) {
    b->blkmapctr++; 
  }
  else if ( status & RETR_HITS_CACHED ) {
    s_log ( s->debug, L_INFO, NULL, "retreive_hits: pass finished; (hits stored!)" );
    if ( s->batches[level].howmany > 1 ) {
      s_log ( s->debug, L_INFO, NULL, "attempting to re-sort blockmap." );
      (void)blockmap_resort ( s, level ); 
      s_log ( s->debug, L_INFO, NULL, "done" );
    }
  }
  if ( status & RETR_RESMAP_FULL ) {
    return RETR_RESMAP_FULL;
  }
  if ( status & RETR_END_OF_MAP ) {
    s_log ( s->debug, L_INFO, NULL, "retreive_hits: end of map reached; returning." );
    return RETR_END_OF_MAP;
  }
  s_log ( s->debug, L_INFO, NULL, "returning 0" );
  return 0;
}

Z32 process_block_unit ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res )
{
  N8  type = w->type; 
  /* what kind of blockunit is it? */
  if ( type ) {
    /* a block of hits? */
    s_logf ( s->debug, L_INFO, "block unit processing: entry %d;", n ); 
    if ( s->batches[bn].not_op ) {
	return process_hit_block_booleannot ( s, bn, w, n, map, res );
    }
    return process_hit_block ( s, bn, w, n, map, res );
  }
  else {
    /* or a single low-freq word? */
    if ( s->batches[bn].not_op ) {
	return process_single_entry_booleannot ( s, bn, w, n, map, res );
    }
    return process_single_entry ( s, bn, w, n, map, res );
  }
}

Z32 process_hit_block ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res )
{
  Z32 status;
  N32 howmany; 
  Gmap hits = NULL;
  /* before we do anything else, we should check if we have cached hits
     stored in this block:*/
  if ( w->n_cached ) {
    s_logf ( s->debug, L_INFO, "found %d stored hits; processing.", w->n_cached ); 
    /* this is not supposed to happen: 
       we should never get to another (next?) block while we still
       have indices cached from this one! */
    if ( w->blk_cached != n ) {
      s_logf ( s->debug, L_ERROR, "found cached hits from block %d,", w->blk_cached ); 
      s_logf ( s->debug, L_ERROR, "while processing block %d.", n ); 
      return RETR_BUMMER;
    } 
    hits = retreive_cached_hits ( s, bn, w, n, map, &howmany ); 
  }
  else {
    s_logf ( s->debug, L_INFO, "retreiving hit block for entry %d;", n ); 
    hits = retreive_hit_block ( s, bn, w, n, map, &howmany ); 
    s_logf ( s->debug, L_INFO, "%d hits retreived;", howmany ); 
  }
  if ( ! hits ) {
    s_log ( s->debug, L_INFO, NULL, "block does not contain any potential hits (completely below the lower map bounday); marking the block clean; returning."); 
    return RETR_BLK_CLEAN;
  }
  if ( hits == (Gmap)-1 ) {
    s_log ( s->debug, L_INFO, NULL, "retreive_hit_block returned -1; END_OF_MAP reached; returning." ); 
    return RETR_END_OF_MAP;
  }
  if ( map ) {
    s_log ( s->debug, L_INFO, NULL, "filtering the retreived hits against the search map;" ); 
    status = filternload_hits ( s, bn, w, n, map, hits, howmany, res ); 
    s_logf ( s->debug, L_INFO, "ATTENTION: filternload returned %d;", status ); 
  }
  else {
    /* load the whole block on the result map! */
    s_log ( s->debug, L_INFO, NULL, "loading the hits retreived without filtering;" ); 
    status = load_hits ( s, hits, howmany, res );
    status |= RETR_BLK_CLEAN;
  } 
  old_Gmap ( hits ); 
  return status;
}

Gmap retreive_cached_hits ( Search s, N8 bn, Word w, N32 n, Gmap map, N32 *howmany )
{
  Gmap hits = NULL;
  Z32 *map_ptr;
  Z32 map_pos;

  if ( map ) {
    map_pos = map->gm_c;
    s_logf ( s->debug, L_INFO, "retreiving cached; search map position: %d", map->gm_c );      
    map_ptr = gm_get_cur_pos ( map ); 
      /* if the whole block is completely beyond the map boundary,
	 we are not interested in it; */
    while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, (Z32 *)&w->cached[0], s->hit_def, bn) < 0 ) {
      if ( !gm_inc_pos ( map ) ) {
	s_logf ( s->debug, L_INFO, "reached the end of map while FF-ing to the begining of the next (cached) block; map pos. %d", map->gm_c );
	s_logf ( s->debug, L_INFO, "map index 0=%d", map_ptr[0] );
	s_logf ( s->debug, L_INFO, "map index 1=%d", map_ptr[1] );
	s_logf ( s->debug, L_INFO, "map index 2=%d", map_ptr[2] );
	return (Gmap)-1;
      }
      map_ptr = gm_get_cur_pos ( map ); 
    }
    /* if it's completely below, we don't need it either... */
    if ( n < w->blkcount - 1 &&  s->hit_def->levels[bn].h2m_cmp_func( map_ptr, gm_get_pos ( w->dir, n+1 ), s->hit_def, bn) > 0 ) {
      w->n_cached   = 0;
      w->cached     = NULL;
      w->blk_cached = -1;
      return NULL;
    }
    /* rewind the map back to where we started searching: */     
    gm_set_pos ( map, map_pos ); 
  }
  else {
    s_log ( s->debug, L_INFO, NULL, "retreiving; (no map)" ); 
  }
  hits          = new_Gmap ( 0, s->hit_def->fields ); 
  hits->gm_h    = w->cached; 
  hits->gm_l    = w->n_cached; 
  *howmany      = w->n_cached;
  w->n_cached   = 0;
  w->cached     = NULL;
  w->blk_cached = -1;
  return hits;
}

Gmap retreive_hit_block ( Search s, N8 bn, Word w, N32 n, Gmap map, N32 *howmany )
{
  Z32 status;
  Z32 *map_ptr;
  Z32 map_pos;
  Gmap hits = NULL;
  *howmany = 0; 
  s_logf ( s->debug, L_INFO, "retreive_hit_block: entry %d", n ); 

  if ( map ) {
    map_pos = map->gm_c; 
    s_logf ( s->debug, L_INFO, "retreiving; search map position: %d", map_pos ); 
    s_logf ( s->debug, L_INFO, "search map factor: %d", map->gm_f); 
    s_logf ( s->debug, L_INFO, "search map length: %d", map->gm_l); 

    map_ptr = gm_get_cur_pos ( map ); 
    s_logf ( s->debug, L_INFO, "element on the map: %d", map_ptr[0] ); 
    /*  if the whole block is completely beyond (above) the map boundary,
	 we are not interested in it; */
    while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( w->dir, n ), s->hit_def, bn) < 0 ) {
      /* big fat warning!! if the above IS the case, we SHOULDN't discard
	 this block; we should simply stop searching, 
	 but this blockunit should be kept for next iteration (unless
	 the batch is completely done... */
      map_pos = map->gm_c; 
      if ( !gm_inc_pos ( map ) ) {
	return (Gmap)-1;
      }
      map_ptr = gm_get_cur_pos ( map ); 
    }
    /*  if it's completely below, we don't need it either...*/
    if ( n < w->blkcount - 1 && 
	 s->hit_def->levels[bn].h2m_cmp_func( map_ptr, gm_get_pos ( w->dir, n+1 ), s->hit_def, bn) > 0 ) {
      w->offset+=s->db->dbspec->block_size;
      return NULL;
    }  
    /* rewind the map back to where it is still below the lower
       boundary of the hit block: */
    gm_set_pos ( map, map_pos ); 
  }
  else {
    s_log ( s->debug, L_INFO, NULL, "retreiving; (no map)" ); 
  }
  s_logf ( s->debug, L_INFO, "calling gethits on map block %d;", n ); 
  hits = new_Gmap ( 0, s->hit_def->fields );
  hits->gm_h =  hit_gethits ( s->db,w->type, gm_get_pos ( w->dir, n ), w->offset, howmany );
  hits->gm_l =  *howmany; 
  s_logf ( s->debug, L_INFO, "gethits got us %d hits;", (*howmany) );
  w->offset+=s->db->dbspec->block_size;
  return hits; 
}

Z32 filternload_hits ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap hits, N32 howmany, Gmap res ) 
{
  Z32 status = 0;
  Z32 put_status = 0; 
  Z32 *map_ptr;
  Z32 *res_ptr;
  Z32 ctr;       
  Z32 map_pos;
  Z8 logmesg[256];
  
  /* OK, here's the logic of what we are doing: 
     we have a block ("hits") of <howmany> hits; we also have a map, 
     either a search corpus, or search results from the previous 
     level. We only need the hits that match the objects on 
     the map (based on the search criteria, hitcmp_func/hitcmp_obj); */
  
  map_pos = map->gm_c;
  /*for ( ctr = 0; ctr < howmany; ctr++ )*/
  ctr = 0;
  while ( ctr < howmany ) {
    map_ptr = gm_get_cur_pos ( map );
    /* so, first we FF the map until we find an object that is
       actually "larger" or "equal" (based on our comparison
       function) than the next hit on the block;  */
    while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos( hits, ctr), s->hit_def, bn ) ) {
      while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos( hits, ctr), s->hit_def, bn ) < 0 ) { 
	/* of course, if we've reached the end of the map before
	   we found any matching hits, that means there's nothing
	   of interest for us in this block. However, we *can't return*
	   just yet -- even though there's nothing in the block we 
	   could use right away, there might be hits in it that 
	   will match something on another map in the next iteration --
	   i.e., if this is only a partial map. */
	if ( !gm_inc_pos ( map ) ) {
	  status |= RETR_END_OF_MAP;
	  s_log ( s->debug, L_INFO, NULL, "END OF MAP reached while filtering;" ); 
	  break;
	}
	map_ptr = gm_get_cur_pos ( map );
      }
      if ( status & RETR_END_OF_MAP ) break;
      /* and now we have to FF the hit list until we find a hit
	 that's less or equal than the current map object; thus, 
	 continuing alternating between these 2 loops, we are going
	 to either find a match, or reach the end of either the map
	 or the hit block.*/
      while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( hits, ctr ), s->hit_def, bn ) > 0 ) {
	ctr++;
	/* again, if we have reached the end of the block before
	   we found an exact match -- there's nothing (left) for us
	   in this block and it is safe to mark the block as "clean". */
	if ( ctr == howmany ) {
	  status |= RETR_BLK_CLEAN;
	  break;
	}
      }
      if ( status & RETR_BLK_CLEAN ){
	break;
      }
    }
    if ( ( status & RETR_END_OF_MAP ) || ( status & RETR_BLK_CLEAN ) ) break;
    /* And now, the matches. Note, that there can be more than one
       element from the map that matches this hit! For example, we
       are searching for co-occurences of "a" and "the"; the map
       already contains 3 different occurences of "a" in this
       sentence. The hit for "the" that we have just found makes *3*
       co-occurences with the 3 hits above. Of course, if there's
       another "the" in the sentence, then it makes 3 more
       cooccurences with those 3, so while we are packing these hits
       away, we don't want to FF the map permanently -- we have to
       start from this spot with the next hit from the list in the
       next iteration. */
    while ( !s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( hits, ctr), s->hit_def, bn ) ) {
      res_ptr = gm_get_eod ( res );
      put_status = hit_put ( gm_get_pos ( hits, ctr), map_ptr, res_ptr, s->hit_def, bn );
      gm_inc_eod ( res );
      if ( map_ptr >= ( map->gm_h + map->gm_eod * map->gm_f ) ) break;
      map_ptr += map->gm_f;        
    }
    ctr++;
    /* the search map will be FF-ed during the next loop iteration; */
  }
  /* If we have finished the entire hitblock, depending on how it 
     happened (whether the last hit in the block was a match or not)
     we might have not detected the fact; so let's check again: */
  
  if ( ctr == howmany ) {
    s_log ( s->debug, L_INFO, NULL, "REACHED THE END OF HITBLOCK;" );
    status |= RETR_BLK_CLEAN;
  }
  if ( res->gm_eod >= s->batch_limit ) {
    status |= RETR_RESMAP_FULL; 
  }
  /* let's see if we've got any unprocessed hits left: */
  if ( howmany - ctr ) {
    w->blk_cached = n;       
    w->n_cached   = howmany - ctr; 
    w->cached     = (Z32 *) malloc ( w->n_cached * s->hit_def->fields * sizeof (Z32) ); 
    /*
      copy_hits ( w->cached, hits, ctr, w->n_cached ); 
    */
    memcpy ( w->cached, gm_get_pos ( hits, ctr), s->hit_def->fields * w->n_cached * sizeof (Z32) ); 
    status |= RETR_HITS_CACHED;
  }
  gm_set_pos ( map, map_pos ); 
  if ( status & RETR_END_OF_MAP )
    status ^= RETR_END_OF_MAP; /* ! */
  return status; 
}

Z32 load_hits ( Search s, Gmap hits, N32 howmany, Gmap res )
{
  Z32  ctr; 
  Z32 *res_ptr;
  Z32  status;
  s_logf ( s->debug, L_INFO, "loading %d hits w/out filtering", howmany ); 
  for ( ctr = 0; ctr < howmany; ctr++ ) {
    res_ptr = gm_get_eod ( res ); 
    status = hit_put ( gm_get_pos ( hits, ctr ), NULL, res_ptr, s->hit_def, 0 );
    if ( status != res->gm_f ) {
      s_logf ( s->debug, L_ERROR, "wrong number (%d) of indices put on the map", status);
      return RETR_BUMMER;
    }
    else {
      status = 0;
    }
    gm_inc_eod ( res ); 
  }
  if ( res->gm_eod >= s->batch_limit ) {
    status = RETR_RESMAP_FULL; 
  }
  return status;
}

Z32 process_hit_block_booleannot ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res )
{
  Z32 status  = 0;
  N32 howmany = 0; 
  Gmap hits   = NULL;
  /* before we do anything else, we should check if we have cached hits
     stored in this block:*/
  if ( w->n_cached ) {
    s_logf ( s->debug, L_INFO, "found %d stored hits; processing.", w->n_cached ); 
    /*  this is not supposed to happen: 
        we should never get to another (next?) block while we still
        have indices cached from this one! */
    if ( w->blk_cached != n ) {
      s_logf ( s->debug, L_ERROR, "found cached hits from block %d,", w->blk_cached ); 
      s_logf ( s->debug, L_ERROR, "while processing block %d.", n ); 
      return RETR_BUMMER;
    }      
    hits = retreive_cached_hits_booleannot ( s, bn, w, n, map, res, &howmany ); 
  }
  else {
    s_logf ( s->debug, L_INFO, "retreiving hit block for entry %d;", n ); 
    hits = retreive_hit_block_booleannot ( s, bn, w, n, map, res, &howmany ); 
    s_logf ( s->debug, L_INFO, "%d hits retreived;", howmany ); 
  }
  /*  while we were retreiving hit blocks above, we might have put
      something on the result map (even before we get to filtering 
      the results) -- if those hits from the previous level map were
      below the lower boundary of this block; so we have to check our
      results map and see whether it's "full": */
  if ( res->gm_eod >= s->batch_limit ) {
    status = RETR_RESMAP_FULL; 
  }
  if ( ! hits ) {
    s_log ( s->debug, L_INFO, NULL, "boolean not hit retreival: nothing interesting in this block; marking it clean."); 
    return ( status | RETR_BLK_CLEAN );
  }  
  if ( hits == (Gmap)-1 ) {
    s_log ( s->debug, L_INFO, NULL, "retreive_hit_block_booleannot returned -1; END_OF_MAP reached; returning." ); 
    return ( status | RETR_END_OF_MAP );
  }
  s_logf ( s->debug, L_INFO, "boolean not: filtering search map against retreived hits; (map block %d)", n ); 
  status = filternload_booleannot ( s, bn, w, n, map, hits, howmany, res ); 
  s_logf ( s->debug, L_INFO, "filternload_boolean returned %d;", status ); 
  old_Gmap ( hits ); 
  return status;
}

Gmap retreive_cached_hits_booleannot ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res, N32 *howmany )
{
  Gmap hits    = NULL; 
  Z32 *map_ptr = gm_get_cur_pos ( map );
  Z32 *res_ptr = NULL;
  *howmany = 0; 
  s_logf ( s->debug, L_INFO, "retreiving cached/NOT; search map position: %d", map->gm_c );      

  while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, (Z32 *)&w->cached[0], s->hit_def, bn) < 0 ){
    /* PUT HIT ON THE RESULT MAP */
    res_ptr = gm_get_eod ( res ); 
    memcpy ( res_ptr, map_ptr, map->gm_f * sizeof (Z32) );
    gm_inc_eod ( res ); 
    if ( !gm_inc_pos ( map ) ) {
      return (Gmap)-1;
    }
    map_ptr = gm_get_cur_pos ( map ); 
  }
  /* if it's completely below, we simply discard it */      
  if ( n < w->blkcount - 1 && 
       s->hit_def->levels[bn].h2m_cmp_func( map_ptr, gm_get_pos ( w->dir, n+1 ), s->hit_def, bn) > 0 ) {
    w->n_cached   = 0;
    w->cached     = NULL;
    w->blk_cached = -1;  
    return NULL;
  }
  hits          = new_Gmap ( 0, s->hit_def->fields );    
  hits->gm_h    = w->cached; 
  hits->gm_l    = w->n_cached; 
  *howmany      = w->n_cached;
  w->n_cached   = 0;
  w->cached     = NULL;
  w->blk_cached = -1;
  return hits;
}

Gmap retreive_hit_block_booleannot ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res, N32 *howmany )
{
  Z32 status   = 0;
  Z32 *map_ptr = gm_get_cur_pos ( map );
  Z32 *res_ptr = NULL;
  Z32 map_pos  = map->gm_c;  
  Gmap hits;
  Z32 j; 

  *howmany = 0; 
  s_logf ( s->debug, L_INFO, "retreive_hit_block/NOT: entry %d", n ); 
  /*s_logf ( s->debug, L_INFO, "retreive_hit_block/NOT: document %d", ((w->dir)[n].index[0]) ); */
  s_logf ( s->debug, L_INFO, "retreiving/NOT; search map position: %d", map_pos ); 

  /* if the whole block is completely beyond the map boundary,
     we are not interested in it -- that is, for now. 
     But whatever is below the lower boundary of the hitblock on 
     the map is by all means valid result material, so we are 
     going to put it on the result map.  */  

  while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( w->dir, n ), s->hit_def, bn) < 0 ) {
      /* PUT HIT ON THE RESULT MAP */
      res_ptr = gm_get_eod( res ); 
      memcpy( (void *)res_ptr, (const void *)map_ptr, (size_t) map->gm_f * sizeof (Z32) );
      gm_inc_eod( res ); 

      /*if this block of hits is indeed completely outside (beyond)
	the map we should simply left it untouched. Because there may
	or may not be hits matching the objects in this block found in
	the next iteration of the previous search level.  (unless the
	batch is completely done that is).  BUT we can load the entire
	contents of the search map onto the results map!  */
	 
      if ( !gm_inc_pos ( map ) ) return (Gmap)-1;
      map_ptr = gm_get_cur_pos ( map ); 
  }

  map_pos = map->gm_c; 
  s_logf ( s->debug, L_INFO, "retreiving/NOT; search map position (FF-d): %d", map_pos ); 
  /* if it's completely below, we simply discard the block. */

  if ( n < w->blkcount - 1 && 
       s->hit_def->levels[bn].h2m_cmp_func( map_ptr, gm_get_pos ( w->dir, n+1 ), s->hit_def, bn) > 0 ) {
    s_log ( s->debug, L_INFO, NULL, "block completely below the map; returning;" );      
    w->offset+=s->db->dbspec->block_size;
    return NULL;
  }
  s_logf ( s->debug, L_INFO, "calling gethits on map block %d;", n );
  
  hits = new_Gmap ( 0, s->hit_def->fields ); 
  hits->gm_h =  hit_gethits ( s->db,w->type, gm_get_pos ( w->dir, n ), w->offset, howmany );
  hits->gm_l =  *howmany; 
  s_logf ( s->debug, L_INFO, "gethits got us %d hits;", (*howmany) );
  w->offset+=s->db->dbspec->block_size;
  return hits; 
}

Z32 filternload_booleannot ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap hits, Z32 howmany, Gmap res )
{
  Batch b = s->batches + bn; 
  Z32 status     = 0; 
  Z32 put_status = 0; 
  Z32 *map_ptr   = NULL;
  Z32 *res_ptr   = NULL;
  Z32  ctr       = 0;       
  Z32 j          = 0; 
  Z32 *next_block_bndry = NULL; 

  if ( b->blkmapctr < b->blockmap_l - 1 ) {
       if ( b->blockmap[b->blkmapctr+1].w->n_cached &&
	    ( b->blockmap[b->blkmapctr+1].w->blk_cached == b->blockmap[b->blkmapctr+1].n ) ) {
	 next_block_bndry = (Z32 *)b->blockmap[b->blkmapctr+1].w->cached; 
       }
       else {
	 next_block_bndry = gm_get_pos(b->blockmap[b->blkmapctr+1].w->dir, b->blockmap[b->blkmapctr+1].n);
       }
    }

  map_ptr = gm_get_cur_pos ( map ); 
  /* OK, here's the logic of what we are doing here: 

     we have a block ("hits") of <howmany> hits; we also have the map
     from the previous pass. We are searching for hits from the map
     that do not have matches in the hitlists generated on this search 
     level. */

  ctr = 0; 
  if ( s->hit_def->levels[bn].h2m_cmp_func 
       ( map_ptr, gm_get_pos ( hits, ctr), s->hit_def, bn ) < 0 ) {
      /*This should not happen -- we FF-d the map when we retreive the 
	hit block.*/
      s_log ( s->debug, L_ERROR, 
	      NULL, "current map element is BELOW the lower boundary of the hitblock in filternload_booleannot" );      
      return RETR_BUMMER;
  }  
  while ( ctr < howmany ) {
    map_ptr = gm_get_cur_pos ( map ); 
    while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( hits, ctr), s->hit_def, bn ) ) {
      if ( ( b->blkmapctr < b->blockmap_l - 1 )
	   && ( s->hit_def->levels[bn].h2h_cmp_func ( gm_get_pos ( hits, ctr ), next_block_bndry, s->hit_def, bn) >= 0 ) ) { 
	s_logf ( s->debug, L_INFO, "reached the boundary of the next block in filternload_boolean, 2nd loop entry; hit %d.", ctr ); 	
	status |= RETR_REACHED_NEXT_BLOCK_BOUNDARY; 
	break; 
      }
      while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( hits, ctr), s->hit_def, bn ) < 0 ) {
	res_ptr = gm_get_eod ( res ); 
	memcpy ( (void *)res_ptr, (const void *)map_ptr, (size_t) map->gm_f * sizeof (Z32) );
	gm_inc_eod ( res ); 
	
	/*  Now we try to increment the search map;
	    if we've reached the end of the map we should
	    (obviously) stop searching. But we don't want to
	    discard this hitblock just yet; because maybe more
	    matching hits on the previous level will be found
	    during the next iteration. */
	
	if ( !gm_inc_pos ( map ) ) {
	  status |= RETR_END_OF_MAP;
	  s_log ( s->debug, L_INFO, NULL, "END OF MAP reached while filtering w/boolean NOT operator;" ); 
	  break;
	}      
	map_ptr = gm_get_cur_pos ( map ); 
      }
      if ( status & RETR_END_OF_MAP ) {
	break;
      }
      /* and now we have to FF the hit list until we find a hit
	 that's less than or equal the current map object; thus, 
	 continuing alternating between these 2 loops, we are going
	 to either find a match, or reach the end of either the map
	 or the hit block.  */
      
      while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( hits, ctr), s->hit_def, bn ) > 0 ) {
	ctr++; 
	if ( ctr == howmany ) { //if we are at the end of a block...
	  status |= RETR_BLK_CLEAN;
	  break;
	}
	if ( ( b->blkmapctr < b->blockmap_l - 1 ) &&
	     ( s->hit_def->levels[bn].h2h_cmp_func ( gm_get_pos ( hits, ctr), next_block_bndry, s->hit_def, bn) >= 0 ) ) { 
	  s_logf ( s->debug, L_INFO, "reached the boundary of the next block in filternload_boolean; hit %d.", ctr ); 		   
	  status |= RETR_REACHED_NEXT_BLOCK_BOUNDARY; 
	  break; 
	}
      }

      if ( status & RETR_BLK_CLEAN )
	break;      
    }
    if ( ( status & RETR_END_OF_MAP ) || 
	 ( status & RETR_BLK_CLEAN ) || 
	 ( status & RETR_REACHED_NEXT_BLOCK_BOUNDARY) )
      break;

    /* If we are still here, it means that we came across one or more
       matches. We simply skip them. */

    while ( !s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( hits, ctr), s->hit_def, bn ) ) {
      if ( !gm_inc_pos ( map ) ) {
	status |= RETR_END_OF_MAP;
	s_log ( s->debug, L_INFO, NULL, "END OF MAP reached while skipping matching entry (boolean NOT search);" ); 
	break;
      }
      map_ptr = gm_get_cur_pos ( map ); 
    }
    if ( ( status & RETR_END_OF_MAP ) )
      break;
    ctr++;
  }

  if ( ( b->blkmapctr == b->blockmap_l - 1 ) && !( status & RETR_END_OF_MAP ) ) {
    /* it is safe to load the rest of the map onto the result map! */
    while ( 1 ) {
      map_ptr = gm_get_cur_pos ( map ); 
      res_ptr = gm_get_eod ( res ); 
      memcpy ( res_ptr, map_ptr, map->gm_f * sizeof(Z32) );
      gm_inc_eod ( res ); 
      if ( !gm_inc_pos ( map ) ) 
	break;
    }
    status |= RETR_END_OF_MAP;
  }

  /* If we have finished the entire hitblock, depending on how it 
     happened (whether the last hit in the block was a match or not)
     we might have not detected the fact; so let's check again: */

  if ( ctr == howmany ) {
    s_log ( s->debug, L_INFO, NULL, "REACHED THE END OF HITBLOCK;" );
    status |= RETR_BLK_CLEAN;
  }

  if ( res->gm_eod >= s->batch_limit ) {
    status |= RETR_RESMAP_FULL; 
  }
  
  /* let's see if we've got any unprocessed hits left: */
  if ( howmany - ctr ) {
    w->blk_cached = n;      
    w->n_cached   = howmany - ctr; 
    /* w->cached     = (hit *) malloc ( w->n_cached * sizeof( hit ) ); */
    w->cached     = (Z32 *) malloc ( w->n_cached * s->hit_def->fields * sizeof (Z32) );
    /* copy_hits ( w->cached, hits, ctr, w->n_cached ); */
    memcpy ( w->cached, gm_get_pos ( hits, ctr), s->hit_def->fields * sizeof (32) * w->n_cached ); 
    status |= RETR_HITS_CACHED;
  }
  return status; 
}

Z32 process_single_entry ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res )
{
  Z32 *res_ptr;
  Z32  status = 0;
  
  if ( map ) {
    status = filter_single_entry ( s, bn, w, n, map, res );
  }
  else {
    res_ptr = gm_get_eod ( res ); 
    (void)hit_put ( gm_get_pos ( w->dir, n ), NULL, res_ptr, s->hit_def, bn );  
    gm_inc_eod ( res );   
    status |= RETR_BLK_CLEAN;
  }
  return status; 
}

Z32 filter_single_entry ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res )
{
  Z32 status;
  Z32 *map_ptr;
  Z32 *res_ptr;   
  map_ptr = gm_get_cur_pos ( map ); 

  while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( w->dir, n ), s->hit_def, bn) < 0 ) {
    if ( !gm_inc_pos ( map ) ) {
      /*return RETR_BLK_CLEAN | RETR_END_OF_MAP;*/
      return RETR_END_OF_MAP;
    }
    map_ptr = gm_get_cur_pos ( map ); 
  }

  if ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( w->dir, n ), s->hit_def, bn) > 0 ) {
    return RETR_BLK_CLEAN; 
  }
  while (!s->hit_def->levels[bn].h2m_cmp_func (map_ptr, gm_get_pos ( w->dir, n ), s->hit_def, bn)){
      res_ptr = gm_get_eod ( res ); 
      (void) hit_put ( gm_get_pos ( w->dir, n ), map_ptr, res_ptr, s->hit_def, bn );  
      gm_inc_eod ( res ); 
      if (!gm_inc_pos (map) ) {
        return RETR_BLK_CLEAN;
      }
      else {
        map_ptr = gm_get_cur_pos(map);
      }
    }
  return RETR_BLK_CLEAN; 
}

Z32 process_single_entry_booleannot ( Search s, N8 bn, Word w, N32 n, Gmap map, Gmap res )
{
  Batch b = s->batches + bn; 
  Z32 *res_ptr  =  NULL;
  Z32 *map_ptr  =  NULL;  
  Z32  status   =  0;

  s_log ( s->debug, L_INFO, NULL, "processing single boolean NOT entry." );
  if ( !map ) {
    s_log ( s->debug, L_ERROR, NULL, "process_single_entry_boolean called w/out a map" );
    return RETR_BUMMER;
  }
  map_ptr = gm_get_cur_pos ( map ); 
  s_logf ( s->debug, L_INFO, "(word is from document %d)", (w->dir->gm_h[w->dir->gm_f*n]) );
  while ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos (w->dir, n), s->hit_def, bn) < 0 ) {
    res_ptr = gm_get_eod ( res ); 
    memcpy ( res_ptr, map_ptr, map->gm_f * sizeof(Z32) );
    gm_inc_eod ( res ); 
    s_logf ( s->debug, L_INFO, "single boolean NOT entry; %d hits on the results map;", res->gm_eod );
    if ( !gm_inc_pos ( map ) ) {
	return RETR_END_OF_MAP;
    }
    map_ptr = gm_get_cur_pos ( map ); 
  }
  if ( s->hit_def->levels[bn].h2m_cmp_func ( map_ptr, gm_get_pos ( w->dir, n), s->hit_def, bn) > 0 ) {
    status = RETR_BLK_CLEAN; 
  }
  while (!s->hit_def->levels[bn].h2m_cmp_func (map_ptr, gm_get_pos ( w->dir, n), s->hit_def, bn)) {
      /* this means we found one or more matches; we 
	 skip them; */
    if ( !gm_inc_pos ( map ) ) {
      return RETR_END_OF_MAP;
    }
    map_ptr = gm_get_cur_pos ( map ); 
  }

  if ( b->blkmapctr == b->blockmap_l - 1 ) {
      /* it is safe to load the rest of the map onto 
	 the result map! 
	 Plus, we know that we still have something left on the 
	 map -- otherwise, we would have already returned
	 RETR_END_OF_MAP; */
    while ( 1 ) {
      res_ptr = gm_get_eod ( res ); 
      memcpy ( res_ptr, map_ptr, map->gm_f * sizeof(Z32) );
      gm_inc_eod ( res ); 
      s_logf ( s->debug, L_INFO, "(NOT) loading rest of map; %d results;", res->gm_eod );  
      if ( !gm_inc_pos ( map ) ) {
	break;
      }
      map_ptr = gm_get_cur_pos ( map ); 
    }
    status |= RETR_END_OF_MAP;
  }
  status |= RETR_BLK_CLEAN;
  return status; 
}

Z32 chkstatus_EOM ( Z32 status )
{
  return status & RETR_END_OF_MAP;
}

Z32 chkstatus_CACH ( Z32 status )
{
  return status & RETR_HITS_CACHED;
}

Z32 chkstatus_ERR ( Z32 status )
{
  return status & RETR_BUMMER;
}
