// $Id: hitcon.h,v 2.11 2004/05/28 19:22:08 o Exp $
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


/*
  this file provides the constants that define the structure of the
  TLF v.2 occurence index ("hit")
 */


#ifdef HITCON_H
  #error "hitcon.h multiply included"
#else
  #define HITCON_H

/*
  TLF v.2 occurence indices have a fixed-field structure; 
  each occurence index has 9 fields;
 */

  #define INDEX_DEF_FIELDS     9
  #define FIELDS               9

/* 
   The following fields are stored for each occurence: 
 */

  #define INDEX_DEF_DOCUMENT   1  /* document number */
  #define INDEX_DEF_P1         2  /* level 1 part number */
  #define INDEX_DEF_P2         3  /* level 2 part number */
  #define INDEX_DEF_P3         4  /* level 3 part number */
  #define INDEX_DEF_PARAGRAPH  5  /* paragraph number */
  #define INDEX_DEF_SENTENCE   6  /* sentence number */
  #define INDEX_DEF_WORD       7  /* word number */

  #define INDEX_DEF_OFFSET     8  /* byte offset */
  #define INDEX_DEF_PAGE       9  /* page number */

#endif

