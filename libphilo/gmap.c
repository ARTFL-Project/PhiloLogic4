// $Id: gmap.c,v 2.11 2004/05/28 19:22:06 o Exp $
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
#include "gmap.h"

Z32 *gm_get_eod ( Gmap gm )
{

  if ( gm->gm_eod > gm->gm_l - 1 )
    {
      gm->gm_h = (Z32 *)realloc(gm->gm_h, 2 * gm->gm_l*sizeof(Z32)*gm->gm_f); 

      if ( gm->gm_h == NULL )
	{
	  gm->gm_e = GMAP_MALLOCFAIL;
	  gm->gm_l = 0;
	  return NULL; 
	}

      gm->gm_l *= 2; 

    }

    return ( gm->gm_h + gm->gm_eod * gm->gm_f );
}

Z32 gm_set_eod ( Gmap gm, Z32 eod )
{
  return gm->gm_eod = eod; 
}

Z32 gm_inc_eod ( Gmap gm )
{
  if ( gm->gm_eod > gm->gm_l - 1 )
    return 0; 

  gm->gm_eod++;
  return gm->gm_eod; 
}

Z32 *gm_get_cur_pos ( Gmap gm )
{
  return ( gm->gm_h + gm->gm_c * gm->gm_f );
}

Z32 *gm_get_pos ( Gmap gm, N pos )
{
  return ( gm->gm_h + pos * gm->gm_f );
}

Z32 gm_inc_pos ( Gmap gm )
{
  if ( gm->gm_c >= gm->gm_eod - 1 )
    return 0; 

  gm->gm_c++; return 1; 
}

Z32 gm_set_pos ( Gmap gm, N32 pos )
{
  return gm->gm_c = pos; 
}

Gmap new_Gmap ( N32 initlen, N32 factor )
{
  Gmap g = (Gmap) malloc (sizeof(gmap));

  if ( g == NULL )
    return NULL;

  g->gm_f = factor;
  g->gm_c = g->gm_eod = 0;
  g->gm_e = GMAP_OK;

  if ( initlen ) 
    {
      g->gm_h = (Z32 *) malloc (initlen * sizeof(Z32) * factor); 

      if ( g->gm_h == NULL )
	{
	  g->gm_e = GMAP_MALLOCFAIL;
	  g->gm_l = 0;
	  return g;
	}
    }

  g->gm_l = initlen;
  return g; 
}


void old_Gmap ( Gmap m )
{
  /* "old" is the opposite of "new" */

  free (m->gm_h); 
  free (m); 

}



