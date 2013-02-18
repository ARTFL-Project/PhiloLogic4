// $Id: hitcmp_cooc.c,v 2.11 2004/05/28 19:22:08 o Exp $
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
   index ("hit") comparison functions that we define 
   in this module: 
 */ 

/*
   (the declarations are kept here because the functions themselves 
    are never exported; they are called from other modules by references
    that are exported in the hit_cmp_func[] defined at the bottom of 
    this file)
 */

/*
   same story with these; they are exported by ref in hit_cmp_arg[] 
   so we don't need to export the functions themselves in any .h
   files; 
 */

Z32 h2h_cmp_cooc_lowlevel ( Z32 *a, Z32 *b, Z32 depth )
{
  N32 i; 

  for ( i = 0; i < depth; i++ )
    if ( a[i] != b[i] )
      return (a[i] > b[i]) ? 1 : -1;

  return 0; 

}


Z32 h2h_cmp_cooc ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i; 
  hitcmp *h = hit_def->levels+level;

  return h2h_cmp_cooc_lowlevel ( a, b, h->context );
}

Z32 m2m_cmp_cooc ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level )
{
  N32 i = 0; 
  hitcmp *h = hit_def->levels+level;

  if ( a[0] != b[0] )
    return a[0] < b[0] ? -1 : 1;

  i = h->r_context + 1;

  if ( a[i] != b[i] )
    return a[i] < b[i] ? -1 : 1;

  return 0; 

}

Z32 h_size_cooc ( hitdef *hit_def, N8 level )
{
  N8      size;
  hitcmp *h     = hit_def->levels+level;
 
  Z32 context = h->r_context;
 
  size = context + (level + 1)*2 + 1;  

  /*
    the hit always contains N indices from the
    first-level hit, where N = context, plus the page
    number, plus (level + 1) byte offsetes.  
   */
 
  return size;
}

Z8 *get_method_info_cooc ()
{
  Z8 *ret;

  ret = (Z8 *) malloc ( 256 ); 
  sprintf ( (char *)ret, "This is a simple co-occurence search method; (default)." );

  return ret; 
}


Z32 build_search_level_cooc ( hitcmp *h, Z8 *arg, Z32 n_level )
{
  Z32 context;

  /* 
     this is our default search: 
     coocurrence search in sentence context. 
   */

  if ( arg )
    {
      context = atol ((const char *)arg); 
      if ( context < INDEX_DEF_P1 || context > INDEX_DEF_SENTENCE )
	return -1; 
    }
  else
   context = INDEX_DEF_SENTENCE; 


  h[n_level].type = HIT_CMP_COOC;
  
  h[n_level].h2h_cmp_func =    (*h2h_cmp_cooc);
  h[n_level].h2m_cmp_func =    (*h2h_cmp_cooc); 
  h[n_level].m2m_cmp_func =    (*m2m_cmp_cooc); 

  h[n_level].cntxt_cmp_func =  (*h2h_cmp_cooc);

  h[n_level].hitsize_func =    (*h_size_cooc); 

  h[n_level].context  = context;
  h[n_level].r_context = context; 

  h[n_level].distance = 0; 
  h[n_level].n_real   = n_level; 

  h[n_level].opt      = NULL;

  return 0;

}

Z32 hit_cmp_cooc_arg ( hitdef *hit_def, Z8 *arg, Z32 n_levels )
{
  Z32 i; 
  Z32 context;

  Z32 status;

  hitcmp *h = hit_def->levels;

   for ( i = 0; i < n_levels; i++ )
     status |= build_search_level_cooc ( h, arg, i );

  return 0; 
}



