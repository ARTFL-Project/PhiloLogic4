// $Id: blockmap.h,v 2.11 2004/05/28 19:22:06 o Exp $
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


#ifdef BLOCKMAP_H
  #error "blockmap.h multiply included"
#else


  /* 
     block map is an object that contains a pointer to a Word
     object and a counter pointing to the current position on 
     the object map there; by going along this list of blockmap
     objects ("Blockmap") and re-sorting it in the process, we
     conduct the search. 
   */

  #define BLOCKMAP_H

  #ifndef C_H
    #include "c.h"
  #endif

  #ifndef WORD_H
    #include "word.h"
  #endif


  #define BLOCKMAP_BUILT            0
  #define BLOCKMAP_MALLOC_ERROR     1
  #define BLOCKMAP_BUILD_ERROR      2


  typedef struct blockMap_st *blockMap, blockMap_;

  struct blockMap_st
  {
    Word    w;             /* pointer to word object */
    N32     n;             /* map counter in the object above */
    N32     bn;            /* batch (or "level") number */
  };

/*
  extern Z32 build_blockMap( Search, Z32 );
 */

  extern void blockmap_sort (); 

#endif /* #ifdef BLOCKMAP_H */









