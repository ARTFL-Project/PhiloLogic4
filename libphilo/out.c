// $Id: out.c,v 2.11 2004/05/28 19:22:06 o Exp $
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
#include "c.h"
#include "search.h"
#include "out.h"

Z32 dump_hits_out ( Search s, N32 level, Gmap m )
{
  N32 n = m->gm_eod;
  N32 i; 
  s_logf ( s->debug, L_INFO, "dumping out results; (%d hits on map)", n );
  s_logf ( s->debug, L_INFO, "map position set to %d;", m->gm_c ); 
  if ( s->hit_def->output == HIT_OUT_ASCII ) {
    s_log ( s->debug, L_INFO, NULL, (Z8 *)"(output set to ASCII)" );
  }
  for ( i = 0; i < n; i++ ) {
    if ( s->depth_r ) {
	(void) hit_out ( gm_get_pos(m, i), s->hit_def, level, s->depth_r ); 
    }
    else {
	(void) hit_out ( gm_get_pos(m, i), s->hit_def, level, s->depth ); 
    }
    s->n_printed++; 
    if ( ! ( s->n_printed % 100 ) ) {
	fflush( stdout );
    }
    else if ( s->n_printed == s->soft_limit ) {
	  s->batch_limit = DEFAULT_BATCH_LIMIT;
	  fflush( stdout );
    }                                                                             
    if ( s->n_printed == s->print_limit ) {
      fflush( stdout );
      s->exitcode = 111; 
      return SEARCH_PRINT_LIMIT_REACHED;
    }
  }
  fflush( stdout );
  return 0;
}
