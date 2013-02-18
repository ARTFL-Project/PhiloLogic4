// $Id: gmap.h,v 2.11 2004/05/28 19:22:06 o Exp $
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

#ifndef C_H
  #include "c.h"
#endif

#ifdef GMAP_H
  #error "gmap.h multiply included"
#else
  #define GMAP_H

  #define GMAP_OK         0
  #define GMAP_TOOMANY    1
  #define GMAP_MALLOCFAIL 2

  typedef struct gmap  *Gmap, gmap; 

  struct gmap
  {
    N32  gm_f;  /* factor -- i.e., how many integers/hit */
    Z32 *gm_h;  /* hits */
    N32  gm_c;  /* counter, i.e., the current location */
    N32  gm_l;  /* limit, i.e. malloc-ed size of gm_h */
    N32  gm_eod;/* "end of data", i.e., the current length */
    Z32  gm_e;  /* error condition */
  };
 
  extern Gmap new_Gmap ( N32,N32 );
  extern void old_Gmap ( Gmap );
  extern Z32 *gm_get_eod ( Gmap );
  extern Z32  gm_set_eod ( Gmap, Z32 ); 
  extern Z32  gm_inc_eod ( Gmap );
  extern Z32 *gm_get_cur_pos ( Gmap );
  extern Z32 *gm_get_pos ( Gmap, N ); 
  extern Z32  gm_inc_pos ( Gmap ); 
  extern Z32  gm_set_pos ( Gmap, N32 );

#endif






