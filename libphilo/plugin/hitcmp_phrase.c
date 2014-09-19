// $Id: hitcmp_phrase.c,v 2.11 2004/05/28 19:22:08 o Exp $
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

#ifndef HITCMP_H
  #include "hitcmp.h"
#endif

/* 
   this file contains the comparison functions used for "phrase" 
   searches. 
 */ 

/*
   (the declarations are kept here because the functions themselves 
    are never exported; they are called from other modules by references
    that are exported in the hit_cmp_func[] defined at the bottom of 
    this file)
 */

Z32 hit_wn_phrase_check   (); 

Z32 h2h_cmp_phrase_lowlevel ( Z32 *a, Z32 *b, Z32 depth )
{
  N32 i; 

  for ( i = 0; i < depth; i++ )
    {
      if ( a[i] != b[i] )
	{
	  return (a[i] > b[i]) ? 1 : -1;
	}
    }

  return 0; 

}


Z32 h2h_cmp_phrase_word ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i; 
  hitcmp *h = hit_def->levels+level;

  return h2h_cmp_phrase_lowlevel ( a, b, INDEX_DEF_WORD );
}

Z32 h2h_cmp_phrase_sent ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i; 
  hitcmp *h = hit_def->levels+level;

  return h2h_cmp_phrase_lowlevel ( a, b, INDEX_DEF_SENTENCE );
}

Z32 m2m_cmp_phrase ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i = 0; 
  hitcmp *h = hit_def->levels+level;

  if ( a[0] != b[0] )
    return a[0] < b[0] ? -1 : 1;

  /*
    "context" of a phrase search is always INDEX_DEF_SENTENCE; 
     so in the map entry we have INDEX_DEF_SENTENCE indices, then 
     the page number, THEN THE WORD NUMBER and only then, the 
     BYTE OFFSET -- by which we actually want to sort the map:
   */

  i = h->r_context + 2;
  i = INDEX_DEF_WORD + 1;

  if ( a[i] != b[i] )
    return a[i] < b[i] ? -1 : 1;

  return 0; 

}

Z32 h2m_wn_phrase_check ( Z32 last, Z32 new, hitdef *h, Z32 level )
{
  Z32 res; 
  N32 last_real_level = level - 1; 

  N32 phrase_distance = h->levels[level].distance; 
  Z32 target_distance; 

  if ( h->depth_r && ( level >= h->depth_r ) )
    last_real_level = h->depth_r - 1; 

  target_distance =
    ( h->levels[level].n_real - h->levels[last_real_level].n_real ) 
    * phrase_distance; 

  res = new - last; 

  if ( res == target_distance )
    return 0; 

  if ( res < target_distance )
    return 1; 

  return -1;
}


Z32 h2m_cmp_phrase ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i; 
  hitcmp *h = hit_def->levels+level;
  Z32 res;

  /*
    if the 2 words are not even in the same sentence, then
    they are surely not in the same phrase: 
   */
  if ( res = h2h_cmp_phrase_sent ( a, b, hit_def, level ) )
    return res; 

  /* let's figure out the location of the word on the map: */

  if ( hit_def->depth_r && ( level >= hit_def->depth_r ) )
    i = h->r_context + (hit_def->depth_r - 1 ) * 2 + 1; 
  else
    i = h->r_context + (level - 1 ) * 2 + 1; 

  return h2m_wn_phrase_check ( a[i], b[INDEX_DEF_SENTENCE], hit_def, level );
}




Z32 h_size_phrase ( hitdef *hit_def, N8 level )
{
  N8      size;

  hitcmp *h     = hit_def->levels+level;
 
  Z32 context = h->r_context;
 
  size = context + (level + 1)*2 + 1; 

  /*
    the hit always contains N indices from the
    first-level hit, where N = context, plus the page
    number, plus (level + 1) byte offsets and word numbers  
   */
 
  return size;
}

Z8 *get_method_info_phrase ()
{
  Z8 *ret;

  ret = (Z8 *) malloc ( 256 ); 
  sprintf ( (char *)ret, "This is a PHRASE search method." );

  return ret; 
}

Z32 build_search_level_phrase ( hitcmp *h, Z8 *arg, Z32 n_level )
{
  Z32 context;
  Z32 distance = 1; 
  
  if ( arg )
    {
      distance = atol ((const char *)arg); 
      if ( !distance )
	return -1;
    }

  context = INDEX_DEF_SENTENCE; 


  h[n_level].type = HIT_CMP_PHRASE;
  
  h[n_level].h2h_cmp_func =    (*h2h_cmp_phrase_word);
  h[n_level].h2m_cmp_func =    (*h2m_cmp_phrase); 
  h[n_level].m2m_cmp_func =    (*m2m_cmp_phrase); 

  h[n_level].cntxt_cmp_func =  (*h2h_cmp_phrase_sent);

  h[n_level].hitsize_func =    (*h_size_phrase); 

  h[n_level].context  = context;
  h[n_level].r_context = context; 

  h[n_level].distance = distance; 
  h[n_level].n_real   = n_level; 

  h[n_level].opt      = NULL;

  return 0;

}

Z32 hit_cmp_phrase_arg ( hitdef *hit_def, Z8 *arg, Z32 n_levels )
{
  Z32 i; 
  Z32 context;

  Z32 status;

  hitcmp *h = hit_def->levels;

  for ( i = 0; i < n_levels; i++ )
    status |= build_search_level_phrase ( h, arg, i );

  return 0; 
}



