// $Id: c.h,v 2.12 2004/05/28 19:22:06 o Exp $
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

#ifdef C_H
  #error "c.h multiply included"
#else
  #define C_H
#include <stdint.h>

typedef uint8_t                 N1, N2, N3, N4, N5, N6, N7, N8;
typedef char                   Z8;
typedef uint16_t                N16;
  typedef int16_t                  Z16;
  typedef uint32_t                 N24, N32, N;
  typedef int32_t                   Z24, Z32;
  typedef int                           Z;
  typedef uint8_t                  *String;
  typedef uint64_t            N64;

  /*  Make sure we can define a function that is shadowed by a macro:
      we use this by defining "foo FUNCTION(args)", thereby suppressing
      the macro call interpretation of foo(args).
  */
  #define FUNCTION
  
#endif

#define HITLIST_LIMIT_EXCEEDED          111


