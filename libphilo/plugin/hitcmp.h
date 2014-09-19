// $Id: hitcmp.h,v 2.11 2004/05/28 19:22:08 o Exp $
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

#ifdef HITCMP_H
  #error "hitcmp.h multiply included"
#else
  #define HITCMP_H

  #ifndef STDIO_H
    #include <stdio.h>
    #include <stdlib.h>
  #endif

  #ifndef C_H
    #include "../c.h"
  #endif

  #ifndef HITCON_H
    #include "hitcon.h"
  #endif

  typedef struct hitcmp_st hitcmp; 

  #ifndef HITDEF_H
    #include "hitdef.h"
  #endif

  struct   hitcmp_st
  {
    Z32   (*h2h_cmp_func)  (Z32 *, Z32 *, hitdef *, Z32);
    Z32   (*h2m_cmp_func)  (Z32 *, Z32 *, hitdef *, Z32);
    Z32   (*m2m_cmp_func)  (Z32 *, Z32 *, hitdef *, Z32);

    Z32   (*h2h_sort_func)  (Z32 *, Z32 *, hitdef *, Z32);
    Z32   (*h2m_sort_func)  (Z32 *, Z32 *, hitdef *, Z32);

    Z32   (*cntxt_cmp_func)(Z32 *, Z32 *, hitdef *, Z32);
    Z32   (*h2m_cntxt_cmp_func)(Z32 *, Z32 *, hitdef *, Z32);

    Z32   (*h2m_put_func) (Z32 *, Z32 *, Z32 *, hitdef *, Z32);
    Z32   (*hitsize_func)  (hitdef *, N8);

    void   *config;
    void   *opt;

    N8      type;

    N8      context;
    N8      s_context;
    N8      r_context;

    N8      merge;

    N8      distance;

    N8      n_level; 
    N8      n_real;

    N8      boolean_op;
 
  };

  #define  HIT_CMP_COOC   1
  #define  HIT_CMP_PHRASE 2
  #define  HIT_CMP_PROXY  3
  #define  HIT_CMP_SENTENCE 4

  #include "hitcmp_cooc.h"
  #include "hitcmp_phrase.h"
  #include "hitcmp_proxy.h"
  #include "hitcmp_sent.h"

  #define  HIT_CMP_ARGZ_USAGE "{SEARCH OPTIONS} are: \
           (cooc[:context]|phrase[:distance]|proxy[:distance])"

#endif




