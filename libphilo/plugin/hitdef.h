// $Id: hitdef.h,v 2.11 2004/05/28 19:22:08 o Exp $
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

#ifdef HITDEF_H
  #error "hitdef.h multiply included"
#else
  #define HITDEF_H
  
  #ifndef C_H
    #include "../c.h"
  #endif

  #ifndef HITCON_H
    #include "hitcon.h"
  #endif

  typedef struct hitdef_st hitdef;

  #ifndef HITCMP_H
    #include "hitcmp.h"
  #endif

  #ifndef METHOD_H
    #include "method.h"
  #endif

  struct   hitdef_st
  {
    N32     depth; 
    N32     depth_r; 

    N32     fields;

    hitcmp *levels;
    N8      output;

    SearchMethodEntry    *searchmethods; /* search methods */
  };
 
  extern hitdef *new_hitdef ( N32 );
  extern void    old_hitdef ( hitdef * );

#endif









