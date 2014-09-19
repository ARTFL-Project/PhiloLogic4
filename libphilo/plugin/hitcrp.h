// $Id: hitcrp.h,v 2.11 2004/05/28 19:22:08 o Exp $
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

#ifdef HITCRP_H
  #error "hitcrp.h multiply included"
#else
  #define HITCRP_H

  #ifndef STDIO_H
    #include <stdio.h>
  #endif

  #define  HIT_CRP_BINARY   0
  #define  HIT_BIN_ASCII    1


  extern Z32 hit_crp_args(hitdef *, Z32 *, Z32 *, Z32, Z8 *);
  Z32 h2h_cmp_crp ( Z32 *a, Z32 *b, hitdef *hit_def, Z32 level );
#endif







