// $Id: hitout.h,v 2.11 2004/05/28 19:22:08 o Exp $
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

#ifdef HITOUT_H
  #error "hitout.h multiply included"
#else
  #define HITOUT_H

  #ifndef STDIO_H
    #include <stdio.h>
  #endif

  #define  HIT_OUT_BINARY   0
  #define  HIT_OUT_ASCII    1

  #define  HIT_OUT_ARGZ_USAGE  "{PRINT OPTIONS} are: \
           (a[scii*]|b[inary*])"

  #define  hitout_size(c,n) (sizeof(Z16)*(c<INDEX_DEF_SENTENCE?c:c-1)+n*sizeof(Z32))

  extern Z32 hit_out();
  extern Z32 hit_out_args(hitdef *, Z8 *);

#endif







