// $Id: hitcmp_proxy.c,v 2.11 2004/05/28 19:22:08 o Exp $
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
   this file contains the comparison functions used for "proxy" 
   searches. Proxy searches are essentially the same as phrase 
   searches, except that we are looking for words that occur
   N *or fewer* words from each other. 
 */ 

Z32 hit_wn_proxy_check   (); 

Z32 h2h_cmp_proxy_lowlevel ( Z32 *a, Z32 *b, Z32 depth )
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


Z32 h2h_cmp_proxy_word ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i; 
  hitcmp *h = hit_def->levels+level;

  return h2h_cmp_proxy_lowlevel ( a, b, INDEX_DEF_WORD );
}

Z32 h2h_cmp_proxy_sent ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i; 
  hitcmp *h = hit_def->levels+level;

  return h2h_cmp_proxy_lowlevel ( a, b, INDEX_DEF_SENTENCE );
}

Z32 m2m_cmp_proxy ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
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

Z32 h2m_wn_proxy_check ( Z32 that, Z32 this, hitdef *h, Z32 that_level, Z32 this_level )
{
  Z32 res; 

  N32 phrase_distance = h->levels[this_level].distance; 

  Z32 target_distance =
    ( h->levels[this_level].n_real - h->levels[that_level].n_real ) 
    * phrase_distance;  


  res = this - that; 

  if ( target_distance > 0 )
    {
      if ( res < 0 )
	return 1; 

      if ( res > target_distance ) 
	return -1; 

      if ( res <= target_distance )
	return 0; 
    }
  else
    {
      if ( res > 0 ) 
	return -1; 

      if ( res < target_distance ) 
	return 1; 

      if ( res >= target_distance )
	return 0; 
    }

  return 0; 

}


Z32 h2m_cmp_proxy ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  hitcmp *h = hit_def->levels+level;
  Z32 res = 0;

  N32 real_levels = 0; 

  N32 i, j; 

  /*
    if the 2 words are not even in the same sentence, then
    they are surely not in the same phrase: 
   */
  if ( (res = h2h_cmp_proxy_sent ( a, b, hit_def, level )) )
    return res; 

  if ( hit_def->depth_r && ( level >= hit_def->depth_r ) )
    real_levels = hit_def->depth_r; 
  else
    real_levels = level; 


  for ( j = 0; j < real_levels; j++ ) 
    {

      /* let's figure out the location of the word on the map: */

      i = h->r_context + j * 2 + 1; 

      if ( (res = h2m_wn_proxy_check ( a[i], b[INDEX_DEF_SENTENCE], hit_def, j, level )) )
	return res; 
    }

  return 0;

}


Z32 h_size_proxy ( hitdef *hit_def, N8 level )
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

Z8 *get_method_info_proxy ()
{
  Z8 *ret;

  ret = (Z8 *) malloc ( 256 ); 
  sprintf ( (char *)ret, "This is a PHRASE search method." );

  return ret; 
}

Z32 build_search_level_proxy ( hitcmp *h, Z8 *arg, Z32 n_level )
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


  h[n_level].type = HIT_CMP_PROXY;
  
  h[n_level].h2h_cmp_func =    (*h2h_cmp_proxy_word);
  h[n_level].h2m_cmp_func =    (*h2m_cmp_proxy); 
  h[n_level].m2m_cmp_func =    (*m2m_cmp_proxy); 

  h[n_level].cntxt_cmp_func =  (*h2h_cmp_proxy_sent);

  h[n_level].hitsize_func =    (*h_size_proxy); 

  h[n_level].context  = context;
  h[n_level].r_context = context; 

  h[n_level].distance = distance; 
  h[n_level].n_real   = n_level; 

  h[n_level].opt      = NULL;

  return 0;

}

Z32 hit_cmp_proxy_arg ( hitdef *hit_def, Z8 *arg, Z32 n_levels )
{
  Z32 i; 
  Z32 context;

  Z32 status;

  hitcmp *h = hit_def->levels;

  for ( i = 0; i < n_levels; i++ )
    status |= build_search_level_proxy ( h, arg, i );

  return 0; 
}



