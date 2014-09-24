// $Id: search.c,v 2.11 2004/05/28 19:22:06 o Exp $
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

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <dlfcn.h>
#include <sys/stat.h>
#include "search.h"
#include "out.h"

#include "retreive.h"

Search new_search( dbh *db, Z8 *method, Z8 *arg, int ascii, int limit, int corpussize, char * corpusfile) {
	Search s = malloc( sizeof(Search_) );
	int plugin = 0;
	int j;
	if (limit < 1) {
	  limit = DEFAULT_PRINT_LIMIT;
	}
	if (s == NULL) {
		return NULL;
	}
	s->db = db;
	s->depth		= MAXBATCHES;
	s->depth_r		= 0;
	s->batches		= malloc( sizeof(Batch_) * MAXBATCHES);
	s->hit_def		= new_hitdef( MAXBATCHES ); 
	s->bn			= 0; 
	s->bincorpus	= 1;
	s->corpus		= NULL;
	s->map			= NULL;
	s->debug		= 0; 
	s->print_limit	= limit; 
	s->batch_limit	= DEFAULT_BATCH_LIMIT; 
	s->n_printed	= 0;
	s->soft_limit	= 0;
	s->exitcode		= 0;

	set_search_method(s, method, arg);
	if (ascii) {
		s->hit_def->output = HIT_OUT_ASCII;
	}
	if (corpussize && corpusfile) {
		set_corpus(s,corpusfile,corpussize);
	}
	return s; 
}

int delete_search( Search s) {
  int i;
  int j;
  for (i = 0; i < s->depth; i++) {
    for (j = 0; j < s->batches[i].howmany; j++){
      old_Gmap(s->batches[i].w_list[j].dir);
    }
    free(s->batches[i].w_list);
    free(s->batches[i].blockmap);
  }
  free(s->batches);
  old_hitdef(s->hit_def);
  free(s);
  return 0;
}

int set_corpus( Search s, Z8 *corpuspath, Z32 corpusarg){
  struct stat corpusstat;
  FILE * corpusfile;
  Z32 *buffer;
  Z32 corpussize = (Z32)(corpusarg);
  stat(corpuspath, &corpusstat);
  if (corpusstat.st_size == 0) {
    return 0;
  }
  s->map = new_Gmap ( corpusstat.st_size/(sizeof(Z32)*corpussize), corpussize );
  
  if ( ( s->map->gm_l = hit_crp_args ( s->hit_def, s->map->gm_h, &s->map->gm_f, corpussize, corpuspath ) ) <= 0 ) {
    strcpy ( s->errstr, BAD_CORPUS_ARGZ );
    //Should't return an int here.
    return BAD_ARGZ;
  }
  s->map->gm_eod = s->map->gm_l;
  return 0;
}

int set_search_method( Search s, Z8 *methodstring, Z8* argstring) 
{
  int j;
  int method;
  fprintf(stderr,"search method set to %s\n", methodstring);
  for ( j = 0; s->hit_def->searchmethods[j].sp_tag; j++ ) {
    if ( ! strcmp ( s->hit_def->searchmethods[j].sp_tag, methodstring ) ) {
      method = j;
    }
  }
  for ( j = 0; j < s->depth; j++ ) {
    s->hit_def->searchmethods[method].sp->build_search_level ( s->hit_def->levels, argstring, j );
  }
}

void assign_boolean_op ( Search s, Z32 level, Z32 op )
{
  Z32 i; 
  /*
  for ( i = 0; i < s->depth; i++ ){
    if ( s->hit_def->levels[i].n_real == level ) {
	s->batches[i].not_op = op; 
	break; 
    }
  }
  */
  s->batches[level].not_op = op;
}

/* a perfectly redundant function: :) */
/* well, it used to be perfectly redundant, but it is
   actually here where we want to check if the batch is
   finished.; Arguably, the blockmap manipulations
   (sorting and/or incrementing the blockmap pointer)
   should also be done here and not in retreive.c;*/

Z32 produce_hits ( Search s, N32 level, Gmap map, Gmap res ) 
{
  Z32 code_retreive;
  s_log ( s->debug, L_INFO, NULL, "attempting to retreive hits..." );
  code_retreive = retreive_hits ( s, level, map, res );
  s_logf ( s->debug, L_INFO, "done (code %d returned);", code_retreive );
  if ( code_retreive & RETR_BUMMER ){
      s_log ( s->debug, L_ERROR, NULL, "produce_hits: retreive_hits failed" );
      return SEARCH_BUMMER_OCCURED;
  }
  if ( s->batches[level].blkmapctr >= s->batches[level].blockmap_l ){
    s_log ( s->debug, L_INFO, NULL, "produce_hits: end of BLOCK MAP reached; returning.");
    return SEARCH_BATCH_FINISHED;
  }
  if ( code_retreive & RETR_END_OF_MAP ){
    s_log ( s->debug, L_INFO, NULL, "produce_hits: end of SEARCH MAP reached; returning.");
    return SEARCH_PASS_FINISHED;
  }
  if ( code_retreive & RETR_RESMAP_FULL ){
    s_log ( s->debug, L_INFO, NULL, "produce_hits: batch limit exceeeded; returning.");
    return SEARCH_BATCH_LIMIT_REACHED;
  }
  if ( code_retreive & SEARCH_PRINT_LIMIT_REACHED ){
    return SEARCH_PRINT_LIMIT_REACHED;
    s_log ( s->debug, L_INFO, NULL, "produce_hits: print limit reached; returning");
  }  
  s_log ( s->debug, L_INFO, NULL, "produce_hits: hits produced; returning.");
  return SEARCH_PASS_OK;
}

Gmap map_store_tail ( Search s, N32 level, Gmap r )
{
  Gmap     new = NULL; 
  Batch      B = &s->batches[level];
  blockMap   b = &B->blockmap[B->blkmapctr];
  Word       w = b->w; 
  N32        n = b->n; 
  Z32 *nexthit; 
  N32        c; 
  Z32 *map_ptr; 
  Z32  new_len = 0; 
  Z8   logmesg[256];

  s_logf ( s->debug, L_INFO, "entering store_tail; blockmapctr=%d",B->blkmapctr );

  sprintf ( logmesg, "n_cached=%d", w->n_cached );
  s_log ( s->debug, L_INFO, NULL, logmesg );

  nexthit = w->n_cached ? (Z32 *)w->cached : gm_get_pos ( w->dir, n );
  c = r->gm_eod - 1;
  s_logf ( s->debug, L_INFO, "entering store_tail; counter set to %d",c ); 
  map_ptr = gm_get_pos ( r, c );
  s_logf ( s->debug, L_INFO, "\"next hit\" is in doc %d;", *nexthit );
  s_logf ( s->debug, L_INFO, "map_ptr points to hit in %d;", *map_ptr );

  if ( s->hit_def->levels[level].cntxt_cmp_func == NULL ) {
    s_log ( s->debug, L_ERROR, NULL, "uninitialized context comp. function!" );
  }
  while ( s->hit_def->levels[level].cntxt_cmp_func ( map_ptr, nexthit, s->hit_def, level) >= 0 ) {
    s_log ( s->debug, L_INFO, NULL, "reducing the map counter by 1;" );
    c--; 
    map_ptr = gm_get_pos ( r, c ); 
  }
  s_logf ( s->debug, L_INFO, "%d hits left on the map;", (c+1) );  
  if ( r->gm_eod - c - 1 ){
    s_logf ( s->debug, L_INFO, "creating new map to store %d hits;", (r->gm_eod - c - 1) ); 
    new_len = MAP_INIT_LEN;
    while ( r->gm_eod - c - 1 > new_len ){
      new_len *= 2; 
    }
    s_logf ( s->debug, L_INFO, "length of the new map is %d;", new_len ); 
    new = new_Gmap ( new_len, r->gm_f ); 
    memcpy ( new->gm_h, gm_get_pos(r,c+1), sizeof(Z32)*(r->gm_eod-c-1)*new->gm_f );
    gm_set_eod ( new, r->gm_eod - c - 1); 
    r->gm_h = (Z32 *)realloc (r->gm_h, (c + 1) * sizeof(Z32) * r->gm_f); 
    r->gm_l = c + 1; 
    gm_set_eod ( r, c + 1 );
  }
  else {
    s_log ( s->debug, L_INFO, NULL, "returning NULL map" ); 
  }
  return new;
}

Z32 resmap_sort_func ( const void *a1, const void *a2)
{
  static Search s = NULL; 
  hitcmp h; 
  Gmap tmp;
 
  if ( a1 == NULL ){
    /* initialization: */
    s = (Search)a2;
  }
  else {
    if ( !s ){
      s_log ( L_ERROR, L_ERROR, "%s", "uninitialized map comparison function run attempted" ); 
    }
    h = s->hit_def->levels[s->bn];
    /* return s->hit_def->levels[s->bn].m2m_cmp_func ((Z32 *)a1, (Z32 *)a2, s->hit_def, s->bn); */
    return h.m2m_cmp_func ((Z32 *)a1, (Z32 *)a2, s->hit_def, s->bn);
  }
}

void sort_result_map ( Search s, Gmap m )
{
  /* first, initialize the search function: */
    resmap_sort_func ( NULL, (const void *)s ); 

  /* now we can use it to sort the results: */
  s_logf ( s->debug, L_INFO, "attempting to sort a map of length %d;", m->gm_eod ); 
  qsort ( m->gm_h, m->gm_eod, sizeof(Z32)*(m->gm_f), resmap_sort_func ); 
  s_log ( s->debug, L_INFO, NULL, "(sorted)" ); 
}

/* this one does most of the work for us: */

N32 search_pass ( Search s, N32 bn ) 
{
  Gmap map = s->batches[bn].map;
  Z32   rmf; /* results map factor */
  Z32  code;
  Z32  code_nl; 

  s_logf ( s->debug, L_INFO, "entering search pass, level %d", bn ); 
  /* let's create a map for the search results:*/
  if ( s->batches[bn].not_op ){
    if ( ! map ){
      /* not supposed to happen! */
      /* print an error message here... */
    }
    rmf = map->gm_f; 
  }
  else{
    if ( s->hit_def->levels[bn].hitsize_func == NULL ){
      fprintf ( stderr, "BIG FAT WARNING!! uninitialized hitsize_func;\n" ); 
    }
    rmf = s->hit_def->levels[bn].hitsize_func(s->hit_def, bn);
  }

  s_logf ( s->debug, L_INFO, "initializing results map... (factor %d)", rmf ); 
  s->batches[bn].res = new_Gmap ( MAP_INIT_LEN, rmf ); 
  s_logf ( s->debug, L_INFO, "initialized results map; (factor %d)", rmf ); 

  /* OK, here's the logic of what's going on here: 
     
     First, we search for hits on the current level,
     moving along the blockmap as we go (one block unit
     at a time that is); we are going as far as we can
     -- until we complete the search on the current
     level (in the boundaries of the current search
     Map), OR get too many hits on the Result map: */

  while (( code = produce_hits ( s, bn, map, s->batches[bn].res )) != SEARCH_BUMMER_OCCURED ){
    s_logf ( s->debug, L_INFO, "produce_hits returned %d", code ); 
    if ( code == SEARCH_PASS_OK ){/* just keep retreiving... */
      s_log ( s->debug, L_INFO, NULL, "continuing into next block" ); 
    }
    else {

  /* more interesting stuff begins... this is one of
     the 2 possible cases described above; but for now
     we don't even care if we have completed the
     search, or exceeded the results limit; our primary
     concern is what to do with all the hits we have
     found: */

  /* If this is the last level, then the hits on the
     Result map are the final results and can be
     printed, so we can simply dump them out (though
     we have to watch for the Print Limit)*/
     
  /* If this is not the last level, we have to run
     the next level search using the results of the
     search we've just completed ourselves (Result map)
     as the Search Map for the next level search.*/

  /* In any event, we sort the map first:*/
	  
      if ( s->batches[bn].howmany > 1 ){
	s_log ( s->debug, L_INFO, NULL, "sorting results map;" );
	sort_result_map ( s, s->batches[bn].res );
      }
      else{
	s_log ( s->debug, L_INFO, NULL, "processing results w/out sorting;" ); 
      }   
  
  /* HOWEVER, */

  /* before we can do either of the above, some map
     magic has to be performed.  We cannot use the
     *entire* result map as the Search map for the next
     level search and neither can we print this map out
     as the search result if this is the bottom level;
     because we might still have hits on this level, in
     the unprocessed portion of our blockmap, that
     occur in the same <CONTEXT> objects as the hits in
     the tail of the present result map. So if these
     results get dumped out we can't guarantee that all
     the results are sorted properly; if we use these
     results as the search map, we are likely to lose
     some cooccurences. so we have to chop this tail
     off and save it for the next iteration (assuming,
     of course, we haven't reached the end of blockmap
     yet).*/

      if ( s->batches[bn].howmany > 1 && ( bn < s->depth - 1 ) && ( code != SEARCH_BATCH_FINISHED ) ){
	s_log ( s->debug, L_INFO, NULL, "attempting to store res map tail;");
	s->batches[bn].stored = map_store_tail ( s, bn, s->batches[bn].res );
      }
      if ( s->batches[bn].stored ){
	s_logf ( s->debug, L_INFO, "done; (%d hits stored)", s->batches[bn].stored->gm_eod ); 
      }
      else{
	s_log ( s->debug, L_INFO, NULL, "proceeding with the res. map intact" ); 
      }
      gm_set_pos ( s->batches[bn].res, 0 ); 
      /*gm_rewind ( res );*/
      s_logf ( s->debug, L_INFO, "result map position set to %d", s->batches[bn].res->gm_c ); 
      s_logf ( s->debug, L_INFO, "%d hits on the result map", s->batches[bn].res->gm_eod ); 

      if ( s->batches[bn].res->gm_eod ) {
	if ( bn == s->depth - 1 ) {
	  s_log ( s->debug, L_INFO, NULL, "attempting to dump hits out" );
	  code_nl = dump_hits_out ( s, bn, s->batches[bn].res ); 
	  old_Gmap ( s->batches[bn].res ); 
	  s_log ( s->debug, L_INFO, NULL, "hits printed; returning." );
	}
	else {
	  /* we run the next level search; */

	  /* the results ("hits") found in the next
	     iteration are going to be larger than
	     in the current one; because some parts
	     of the indices found in the next
	     iteration are going to be appended to
	     the hits found while searching the
	     current batch;
	     since we ("the search engine") don't really
	     know anything about the structure of our
	     "hits", let's ask someone who knows:*/

	  /* let's run it! When it returns, we are
	     guaranteed that everything that was
	     there to be found on the lower levels 
	     has been found; it might've taken them
	     a godzillion iterations, but we don't
	     really care:  */

	  s->batches[bn + 1].map = s->batches[bn].res; 
	  code_nl = search_pass ( s, bn + 1 );  
	  old_Gmap ( s->batches[bn].res );	  
	}
       
	if ( code_nl == SEARCH_BUMMER_OCCURED ) {
	  return SEARCH_BUMMER_OCCURED;
	}
	/* if <PRINT_LIMIT> hits have been printed,
	   there's nothing left for us to do: */

	if ( code_nl == SEARCH_PRINT_LIMIT_REACHED ) {
	  return SEARCH_PRINT_LIMIT_REACHED;
	}
      }

      /* otherwise we can continue searching; 
	 (if there's anything left on the blockmap, that is)*/

      if ( code == SEARCH_PASS_FINISHED || code == SEARCH_BATCH_FINISHED ) {
	s_log ( s->debug, L_INFO, NULL, "this level is finished; returning.");
	return SEARCH_PASS_FINISHED;
      }	  

      /*and not forget about the hits we cached
	before we ran the lower-level search:*/	      
	      
      if ( s->batches[bn].stored ){
	s_logf ( s->debug, L_INFO, "found stored results (%d hits)", s->batches[bn].stored->gm_eod ); 
	s->batches[bn].res = s->batches[bn].stored;
	s->batches[bn].stored = NULL;
      }
      else {
	s->batches[bn].res = new_Gmap ( MAP_INIT_LEN, rmf ); 
	s_logf ( s->debug, L_INFO, "initialized results map, again; (factor %d)", rmf ); 
      }
    }
  }

  /* we should never really get here, should we? */
  /* unless some kinda bummer occured: */

  return SEARCH_BUMMER_OCCURED;
}


