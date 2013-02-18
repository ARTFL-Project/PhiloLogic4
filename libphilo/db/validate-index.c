// $Id: validate-index.c,v 2.10 2004/05/28 19:22:04 o Exp $
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../c.h"
#include "unpack.h"

void  readhit ( Z8 *s, hit *h )
   {
      Z8   *t;
      N32   i;

      t = s;

      for ( i = 0; i < FIELDS; i++ )
         {
            h->obj[i] = atoi ( t );
            t = index(t, ' ') + 1;
         }

   }


void check(char *word_read, hit hit_read, char *word_stored, hit hit_stored)
  { unsigned i,j;

    if (strcmp(word_read, word_stored))
      { 
	fprintf(stderr, "Error in index: %s / %s\n", word_read, word_stored);
	exit(1);
      }
    for (i = 0; i < FIELDS; i++)
      if (hit_read.obj[i] != hit_stored.obj[i])
	{ 
	  fprintf ( stderr, "Error in index: %s <", word_read );

	  for ( j = 0; j < FIELDS; j++ )
	    fprintf ( stderr, "%d ", hit_read.obj[j] );

	  fprintf ( stderr, "> / <");

	  for ( j = 0; j < FIELDS; j++ )
	    fprintf ( stderr, "%d ", hit_stored.obj[j]);

	  fprintf ( stderr, ">\n" );

	  /*exit(1);*/
	}
  }


int main()
  { int i,j;
    Z8 *s, key_word[1024], word[1024];
    hit h;
    hit  *hitarray,  *hitblk;
    Z32 type, freq, blkcount, blknum;
    N64 offset;
    int tablesize;

    while ( fgets (key_word, 1024, stdin) )
      { 
	s = index (key_word, ' ') + 1;
	key_word [ s - key_word - 1 ] = '\0';

	readhit (s, &h);

	strcpy(word, key_word);

	hitarray = lookup(key_word, &type, &freq, &blkcount, &offset);
/*
   fprintf (stderr, "frequency: %d\n", freq);
 */
	if (type == 0)
	  { 
	    for (i = 0; i < freq; i++)
	      { if ( i )
		  { 
		    if ( !fgets(key_word,1024,stdin) )
		      {
			fprintf(stderr, "Unexpected end of file at %s\n", key_word);
			exit(1);
		      }

		    s = index (key_word, ' ') + 1;
		    key_word [ s - key_word - 1 ] = '\0';

		  }

		readhit (s, &h);

		check(key_word, h, word, hitarray[i]);
	      }
	  }
	else
	  { 
	    for ( i = 0; i < blkcount; i++ )
	      { 
		hitblk = gethits(type, hitarray[i], offset, &tablesize);
/*
   fprintf (stderr, "occurences in block: %d\n", tablesize);
 */
		offset += BLK_SIZE;
		for (j = 0; j < tablesize; j++)
		  { 
		    if ( (i || j) )
		      { 
			if ( !fgets(key_word,1024,stdin) )
			  {
			    fprintf(stderr, "Unexpected end of file at %s\n", key_word);
			    exit(1);
			  }
			s = index (key_word, ' ') + 1;
			key_word [ s - key_word - 1 ] = '\0';

			readhit (s, &h);
		      }

		    check(key_word, h, word, hitblk[j]);
		    freq--;
		  }
		free(hitblk);
	      } 
	    if (freq)
	      { fprintf(stderr, "Wrong number of occurrences of %s\n", key_word);
		exit(1);
	      }
	  }
	free(hitarray);
     }
    exit(0);
  }


