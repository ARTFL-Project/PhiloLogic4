// $Id: hitman.c,v 2.11 2004/05/28 19:22:08 o Exp $
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

#include "hitdef.h"

Z32 hit_put ( Z32 *hit, Z32 *mi, Z32 *mo, hitdef *hit_def, N32 bn )
     /*
       Here's what's going on: we have a hit -- *h --
       that we want to put on the *mo -- "map out"; if
       this is not the first iteration, i.e., bn
       ("bn number") > 0, we also have a "map in",
       *mi, that has an entry that the hit we have
       found matches; so we wanna *merge* the 2 and put
       the result onto the result map; the function
       returns the number of (Z32)s put on the map.  
      */
{
  hitcmp *h = hit_def->levels+bn;

  Z32 context = 0;
  Z32 need_wn = h->type > HIT_CMP_COOC ? 1 : 0;

  N32 i = 0;

  context = h->r_context;

  if ( !bn )
    /*
      1st iteration; we simply copy the indices that we are interested in 
      onto the out map: 
     */
    {

      /*
	normal indices: (document, parts, paragraph, sentence...)
       */
  
      for ( i = 0; i < context; i++ )
	mo[i] = hit[i];

      /*
	this is the first bn, so let's throw the page number in too
       */

      mo[context] = hit[INDEX_DEF_FIELDS - 1]; 

      /*
	in "phrase" and "proxy" searches we also need the word number:
       */

      if ( need_wn )
	mo[context + 1] = hit[INDEX_DEF_WORD-1]; 

      /*
	finally, the byte offset:
       */

      mo[context + 1 + need_wn] = hit[INDEX_DEF_FIELDS - 2];

      return ( context + 2 + need_wn ); 
    }

  /* 
     This is not the 1st past; 
     so indices from the previous iteration:
   */
	  
  for ( i = 0; i < context + 1 + bn * (need_wn + 1); i++ )
    {
      mo[i] = mi[i];
    }

  /* 
     and then the indices for the word we've just found:
     (if it's a simple co-occurence search, we only need the byte offset;
     if it's a phrase or proxy one, we'll also need the word number)
   */

  if ( need_wn )
    mo[i++] = hit[INDEX_DEF_WORD - 1]; 

  mo[i] = hit[INDEX_DEF_FIELDS - 2];
      
  /* 
     And this is how many integers we've put on the out map: 
     context indices + 1 page number + number of previous interations
     byte offsets + (possibly) number of previous iterations word
     numbers + one more byte offset we've just found + (possibly)
     another word number... uhh!
   */

  return ( context + 2 + bn * (need_wn + 1) + need_wn );

}



