// $Id: word.h,v 2.11 2004/05/28 19:22:06 o Exp $
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


#ifdef WORD_H
  #error "word.h multiply included"
#else

#define WORD_H

#ifndef C_H
  #include "c.h"
#endif

#ifndef HIT_H
  #include "plugin/hit.h"
#endif

#ifndef GMAP_H
  #include "gmap.h"
#endif

#define W_LENGTH_MAX 1024 
#define INITWORDS    1024

typedef struct Word *Word, Word_; 

struct Word
{ 
  /*hit *dir;*/
  Gmap dir; 
 
  N32 type;
  N32 freq;

  N32 blkcount;
  N64 offset;
 
  N32 blkproc;
  /*  hit hitproc;*/
 
  N32 mapctr;

  Z32 blk_cached;  /* block from which hits have been cached */
  N32 n_cached;    /* number of hits cached */
  Z32 *cached;     /* hits cached */
 
};

#endif /* #ifdef WORD_H */






