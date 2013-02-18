// $Id: bitsvector.c,v 2.10 2004/05/28 19:22:04 o Exp $
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
#include <stdlib.h>
#include "bitsvector.h"

bitsvector *bitsvectorNew(N8 *v)
  { bitsvector *r = malloc(sizeof(bitsvector));

    r->v = v;
    r->o = 0;
    r->s = 0;
    r->b = 0;
    return r;
  }

void bitsvectorOld(bitsvector *f)
  { free(f->v);
    free(f);
  }



/*
   N24 bitsvectorGet FUNCTION(Bitsvector f, N5 n) {return bitsvectorGet(f, n);}
*/

N64 bitsvectorGet (bitsvector *f, N8 n)
  {
    N64 ret = 0; 

    N64 buffer = 0; 
    N64 mask = 1; 

    N32 i; 

    N32 o_shift = 0; 

    if ( n > 64 ) 
      {
	fprintf (stderr, "attempted bitsvectorGet on >64 bit integer!\n");
	fprintf (stderr, "whoa! that's a big-ass integer!\n");

	exit (1);
      }

    o_shift = ( n + f->s ) / 8; 

    ret = f->v[f->o]; 

    for ( i = 0; i < o_shift; i++ )
      {
	buffer = f->v[f->o + i + 1]; 
	ret |= (buffer << ( 8 * (i + 1))); 
      }

    ret >>= f->s; 

    mask <<= n; 
    mask--;

    ret &= mask;

    f->o += o_shift; 
    f->s = ( f->s + n ) % 8; 

    return ret; 

  }
