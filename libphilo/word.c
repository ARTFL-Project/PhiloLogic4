// $Id: word.c,v 2.11 2004/05/28 19:22:06 o Exp $
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

#include "word.h"
#include "db/unpack.h"
#ifndef SEARC_H
  #include "search.h"
#endif

Z32 init_wordObject ( Search s, Z8 *word, Word w, N32 *block_n ) 
{
  /*
    it's already malloc-ed somewhere else; we get long
    word lists occasionally and they are malloc-ed in bulk;
   */

  Z32 *tmp; 
  w->type=0;
  w->freq=0;
  w->blkcount=0;
  w->offset=0;
  if (( tmp = hit_lookup (s->db, word, 
		        &(w->type), 
		        &(w->freq), 
		        &(w->blkcount), 
		        &(w->offset)))
      
      == NULL)
    {
      /* not found */
      return 0;
    }

  w->dir        = new_Gmap ( 0, s->hit_def->fields ); 

  w->dir->gm_l  = w->blkcount;
  w->dir->gm_h  = tmp;

  w->mapctr     = 0;
  w->blkproc    = 0; 

  w->blk_cached = -1; 
  w->n_cached   = 0; 
  w->cached     = NULL;

  *block_n = w->type ? w->blkcount : w->freq; 

  return w->freq; 
      
}









