// $Id: hitout.c,v 2.11 2004/05/28 19:22:08 o Exp $
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

#ifndef HITDEF_H
  #include "hitdef.h"
#endif

#ifndef HITOUT_H
  #include "hitout.h"
#endif

Z32 hit_out_ascii (Z32 *m, hitdef *hit_def, Z32 bn, Z32 real_levels)
{
  N32 context;
  N32 wn_skip = 0;

  Z32 i,n;

  hitcmp* h = hit_def->levels+bn;

  context = h->r_context;
//  wn_skip = h->type > HIT_CMP_COOC ? 1 : 0;
  wn_skip = 1;
  n = context;
  n = n == INDEX_DEF_SENTENCE ? n - 1 : n;
  n = h->hitsize_func(hit_def,(Z8)real_levels);
  n = ( context + bn * (wn_skip + 1) + wn_skip );
  /* "normal" objects: */
 
  for ( i = 0; i <= n; i++ )
    printf ("%d ", m[i]);
 
  printf ("%d\n", m[i]);
 	return 1;
  /* finally, the list of byte offsets: */

  i = 1; 

  /*while ( i < bn + 1 )*/
  while ( i < real_levels )
    {
      printf ("%d ", m[context + i*(wn_skip + 1)]);
      i++;
    }

  printf ("%d\n", m[context + i*(wn_skip + 1)]);

  return 1;
}

Z32 hit_out_bin (Z32 *m, hitdef *hit_def, Z32 bn, Z32 real_levels)
{
  N32 context;
  N32 wn_skip = 0;
 
  Z32 i,n;
  Z16 j; 

  N16 doc; 

  hitcmp* h = hit_def->levels+bn;

  context = h->r_context;
//  wn_skip = h->type > HIT_CMP_COOC ? 1 : 0;
  wn_skip = 1;
  n = context;
  n = n == INDEX_DEF_SENTENCE ? n - 1 : n;
  n = ( context + bn * (wn_skip + 1) + wn_skip ); 
  /* "normal" objects: */
  for (i = 0; i <= n + 1; i++) {
  	fwrite(&m[i],sizeof(Z32),1,stdout);
  }
  return 1; 
  doc = (N16) m[0];
  fwrite (&doc, sizeof(N16), 1, stdout);

  for ( i = 1; i < n; i++ )
    {
      j = (Z16) m[i];
      fwrite (&j, sizeof(Z16), 1, stdout);
    }
 
  /* page tag: */

  j = (Z16) m[context];
  fwrite (&j, sizeof(Z16), 1, stdout);


  /* finally, the list of byte offsets: */

 
  for ( i = 1; i < real_levels + 1; i++ )
    fwrite (&(m[context + i*(wn_skip + 1)]), sizeof(Z32), 1, stdout);

  return 1;
}

Z32 hit_out (Z32 *m, hitdef *h, Z32 bn, Z32 real_levels)
{
  if ( h->output == HIT_OUT_ASCII )
    return hit_out_ascii (m, h, bn, real_levels);

  return hit_out_bin (m, h, bn, real_levels);
}

Z32 hit_out_args (hitdef *h, Z8 *arg)
{
  if ( arg[0] == 'B' || arg[0] == 'b' )
    h->output = HIT_OUT_BINARY; 

  else if ( arg[0] == 'A' || arg[0] == 'a' )
    h->output = HIT_OUT_ASCII;

  else 
    return -1; 

  return 0; 
}



