// $Id: bitsvector.h,v 2.10 2004/05/28 19:22:04 o Exp $
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

#ifdef BITSVECTOR_H
  #error "bitsvector.h multiply included"
#else
  #define BITSFILE_H

  #ifndef C_H
    #include "../c.h"
  #endif



  struct Bitsvector
    { N8 *v;
      N32 o;
      N16 s;
      N32 b;
    };

typedef struct Bitsvector bitsvector;

bitsvector *bitsvectorNew(N8 *v);

void bitsvectorOld(bitsvector *f);

N64 bitsvectorGet (bitsvector *f, N8 n);

  #define bitsvectorTell(x)	((((x)->o) << 3) + (x)->s)

  #define bitsfileSeek(x, n)	\
    begin (x)->o = ((n) + (x)->o) >> 3; \
      (x)->s = 0, (Void)bitsvectorGet(x, n & 7); end


  #define bitsvectorGet24(x, n) \
   ( (x)->s < (n) && ( (x)->b >>= 8, (x)->b |= ((x)->v)[((x)->o)++] << 24, (x)->s += 8, \
      (x)->s < (n) && ( (x)->b >>= 8, (x)->b |= ((x)->v)[((x)->o)++] << 24, (x)->s += 8, \
       (x)->s < (n) && ( (x)->b >>= 8, (x)->b |= ((x)->v)[((x)->o)++] << 24, (x)->s += 8) ) ), \
       (x)->s -= (n), ((x)->b >> (32 - (x)->s - (n))) & (1 << (n)) - 1 )

  #define bitsvectorGetBoolean(f)	bitsvectorGet((f), 1)

#endif
