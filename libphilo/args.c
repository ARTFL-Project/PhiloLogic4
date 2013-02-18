// $Id: args.c,v 2.11 2004/05/28 19:22:06 o Exp $
// philologic 2.8 -- TEI XML/SGML Full-text database engine
// Copyright (C) 2004 University of Chicago
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the Affero General Public License as published by
// Affero, Inc.; either version 1 of the License, or\ (at your option)
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
#include <dlfcn.h>
#include <sys/stat.h>
#include <string.h>
#include "args.h"
#include "search.h"

Z32 process_command_argz_backwardcompat ( Search s, Z32 argc, String *argv )
{
  Z32 i,j;
  Z32 method = 0; 

  Z8  engine_arg[256] = "";
  Z8  search_arg[256] = "";
  Z8  *corpus_arg = NULL;
  Z8  output_arg[256] = "";

  Z8  *c = NULL;
  Z8  tok[256];

  N8  distance = 0; 
  N8  context  = 0; 


  for (i = 1; i < argc && argv[i][0] == '-'; i++) {

    switch (argv[i][1]) {

    case 'p':
      sprintf ( search_arg, "phrase" ); 
      if ( isdigit (argv[i][2]) )
	distance = atol (argv[i]+2); 
      break;

    case 'P':
      sprintf ( search_arg, "proxy" ); 
      if ( isdigit (argv[i][2]) )
	distance = atol (argv[i]+2); 
      break;

    case 'S':
      context = atol (argv[i]+2);
      break;

    case 'C':
      corpus_arg = argv[i]+2;
      break;

    case 'A':
      sprintf ( output_arg, "ascii" ); 
      break;
    case 'B':
      sprintf ( output_arg, "binary" ); 
      break;

      /* options 'a' and 'b' are ignored; 
	 only binary corpus is supported!
       */
    case 'a': 
      /*bincorpus = 0;*/
      break;

    case 'b':
      /*bincorpus = 1;*/
      break;

    case 'd':
      if ( strcmp ( engine_arg, "" ) )
	sprintf ( engine_arg, "%s:d=3", engine_arg ); 
      else
	sprintf ( engine_arg, "d=3" ); 
      break;

    case 'L':
      if ( strcmp ( engine_arg, "" ) )
	sprintf ( engine_arg, "%s:L=%d", engine_arg, atol (argv[i]+2) ); 
      else
	sprintf ( engine_arg, "L=%d", atol (argv[i]+2) ); 
      break; 

    case 's':
      if ( strcmp ( engine_arg, "" ) )
	sprintf ( engine_arg, "%s:s=%d", engine_arg, atol (argv[i]+2) ); 
      else
	sprintf ( engine_arg, "s=%d", atol (argv[i]+2) ); 
      /*soft_limit = atol (argv[i]+2);*/
      break;

    case 'l':
      if ( strcmp ( engine_arg, "" ) )
	sprintf ( engine_arg, "%s:l=%d", engine_arg, atol (argv[i]+2) ); 
      else
	sprintf ( engine_arg, "l=%d", atol (argv[i]+2) ); 

      /*batch_limit = atol (argv[i]+2); */
      break; 

    case 'o':
      /*offset = atol (argv[i]+2);*/
      break; 
    }
  }

  if ( engine_arg )
    if ( search_engine_args ( s, engine_arg ) < 0 )
      return BAD_ARGZ;

  /*  
     Then Search method options: 
     if an argument is not supplied, we have some
     sensible defaults that were set when the Search
     object was initialized;
   */

  if ( !strcmp ("", search_arg) )
    strcpy (search_arg, "cooc"); 


  if ( context ) 
    {
      sprintf ( search_arg, "%s:%d", search_arg, context ); 

      if ( distance ) 
	sprintf ( search_arg, "%s:%d", search_arg, distance ); 
    }
  else if ( distance )
    sprintf ( search_arg, "%s:6:%d", search_arg, distance ); 

  
  if ( strcmp ("", search_arg) )
    {
      if ( c = (Z8 *)index ( search_arg, ':' ) )
	{
	  strncpy ( tok, search_arg, c - search_arg ); 
	  tok[c - search_arg] = '\000';
	  c++;
	}
      else
	strcpy ( tok, search_arg ); 

      method = -1; 

      for ( j = 0; s->hit_def->searchmethods[j].sp_tag; j++ )
	{
	  if ( ! strcmp ( s->hit_def->searchmethods[j].sp_tag, tok ) )
	    {
	      /*
		ok, we found the function to process
		options for this kind of search,
		i.e. the rest of the command-line
		argument: 
	       */

	      method = j; 
	      
	    }
	}

      if ( method < 0 )
	{
	  strcpy ( s->errstr, "bad search argument: NO SUCH SEARCH METHOD" );
	  return BAD_ARGZ;
	}
    }

  for ( j = 0; j < s->depth; j++ )
    if ( s->hit_def->searchmethods[method].sp->build_search_level ( s->hit_def->levels, c, j ) )
      {
	strcpy ( s->errstr, "error: search method parameters could not be processed" );
	return BAD_ARGZ;
      }


  /* and then the corpus: */

  if ( argv[i] )
    {
      if ( !corpus_arg )
	strcpy (corpus_arg, "1"); 
 
      if ( ( s->map->gm_l = hit_crp_args ( s->hit_def, s->map->gm_h, &s->map->gm_f, corpus_arg, argv[i] ) ) <= 0 )
	{
	  strcpy ( s->errstr, BAD_CORPUS_ARGZ );
	  return BAD_ARGZ;
	}
      s->map->gm_eod = s->map->gm_l; 
    }

  /* finally, the output specs: */

  if ( strcmp ( output_arg, "" ) )
    {
      if ( hit_out_args ( s->hit_def, output_arg ) )
	{
	  strcpy ( s->errstr, BAD_OUTPUT_ARGZ );
	  return BAD_ARGZ;
	}
    }
  else /* binary is the default */
    if ( hit_out_args ( s->hit_def, "binary" ) )
      {
	strcpy ( s->errstr, BAD_OUTPUT_ARGZ );
	return BAD_ARGZ;
      }

  return 0; 

}


Z32 process_command_argz ( Search s, Z32 argc, String *argv )
{
  Z32 i,j = 0;
  Z8  tok[256];
  Z8  *c = NULL;

  Z32 method = 0; 

  Z8  *engine_arg = NULL;
  Z8  *search_arg = NULL;
  Z8  *corpus_arg = NULL;
  Z8  *output_arg = NULL;
  Z8  *plugin_arg = NULL;

  void *p;
  void *(*gp) (void);
  Z8  filename[256];

  struct stat  cstat;

  for (i = 1; i < argc && argv[i][0] == '-'; i++) 
    {
      switch (argv[i][1]) 
	{
	  /* 
	     'E' specifies upper-level search engine settings: 
	  */

	case 'E':
	  if ( argv[i][2] == ':' )
	    {
	      engine_arg = argv[i] + 3; 
	    }
	  else 
	    {
	      strcpy ( s->errstr, BAD_ENGINE_ARGZ );
	      return BAD_ARGZ;
	    }
	  break; 

	  /* 
	     'S' is for "search"; search arguments are processed by 
	     functions defined in the hit library. The upper-level
	     search engine doesn't really know much about them. 
	  */

	case 'S':
	  if ( argv[i][2] == ':' )
	    {
	      search_arg = argv[i] + 3; 
	    }
	  else
	    {
	      strcpy ( s->errstr, BAD_SEARCH_ARGZ );
	      return BAD_ARGZ;
	    }
	  break; 

	  /* 
	     'corpus': corpus definition process is essentially identical  
	     to specifying search level options, except that it's done for 
	     the 0-level search map supplied on the command line: 
	  */

	case 'C':
	  if ( argv[i][2] == ':' )
	    corpus_arg = argv[i] + 3; 
	  else 
	    {
	      strcpy ( s->errstr, BAD_CORPUS_ARGZ );
	      return BAD_ARGZ;
	    }
	  break; 
	
	  
	/* 
           'P' is for 'print'; this option defines the output format;
	   again, these definitions are in the hit library; the top-level
	   engine doesn't know how our "hits" are structured and how
	   we want them to be formatted.
         */

	case 'P':
	  if ( argv[i][2] == ':' )
	    {
	      output_arg = argv[i] + 3; 
	    }
	  else 
	    {
	      strcpy ( s->errstr, BAD_OUTPUT_ARGZ );
	      return BAD_ARGZ;
	    }
	  break; 

	/* 
           'D' is for 'database plugin'; with this option an alternative
	   plugin could be specified (instead of the builtin ARTFL
	   database search plugin). See the documentation for the
	   detailed explanation of what our "database plugins" are.
         */

	case 'D':
	  if ( argv[i][2] == ':' )
	    {
	      plugin_arg = argv[i] + 3; 
	    }
	  else 
	    {
	      strcpy ( s->errstr, BAD_PLUGIN_ARGZ );
	      return BAD_ARGZ;
	    }
	  break; 
	}
    }

  /* OK, now we have all the arguments, let's process them: */

  /* (in this order!) */

  /* first, the upper-level Search Engine options: */

  if ( engine_arg )
    if ( search_engine_args ( s, engine_arg ) < 0 )
      return BAD_ARGZ;
  /*
  if ( plugin_arg )
    if ( load_plugin ( s, plugin_arg ) < 0 )
      return BAD_ARGZ;
  */
  /*  
     Then Search method options: 
     if an argument is not supplied, we have some
     sensible defaults that were set when the Search
     object was initialized;
   */

  if ( search_arg )
    {
      if ( c = (Z8 *)index ( search_arg, ':' ) )
	{
	  strncpy ( tok, search_arg, c - search_arg ); 
	  tok[c - search_arg] = '\000';
	  c++;
	}
      else
	strcpy ( tok, search_arg ); 

      method = -1; 

      for ( j = 0; s->hit_def->searchmethods[j].sp_tag; j++ )
	{
	  if ( ! strcmp ( s->hit_def->searchmethods[j].sp_tag, tok ) )
	    {
	      /*
		ok, we found the function to process
		options for this kind of search,
		i.e. the rest of the command-line
		argument: 
	       */

	      method = j; 
	      
	    }
	}

      if ( method < 0 )
	{
	  strcpy ( s->errstr, "bad search argument: NO SUCH SEARCH METHOD" );
	  return BAD_ARGZ;
	}
    }

  for ( j = 0; j < s->depth; j++ )
    if ( s->hit_def->searchmethods[method].sp->build_search_level ( s->hit_def->levels, c, j ) )
      {
	strcpy ( s->errstr, "error: search method parameters could not be processed" );
	return BAD_ARGZ;
      }


  /* and then the corpus: */

  if ( corpus_arg )
    {
      
      /* 
	 when corpus arguments are supplied, it implies that the corpus
	 file must also be specified on the command line: 
       */

      if ( ! argv[i] )
	{
	  strcpy ( s->errstr, BAD_CORPUS_ARGZ );
	  return BAD_ARGZ;
	}

      /*fprintf (stderr, "corpus_arg=%s, command line arg=%s\n", corpus_arg, argv[i]); 
      if ( s->map == NULL )
	{
	  fprintf (stderr, "smap not initialized yet; initializing.\n" ); 
	}
      */

      (void) stat(argv[i], &cstat);
      s->map = new_Gmap ( cstat.st_size/(sizeof(Z32)*atol(corpus_arg)), atol(corpus_arg) );

      if ( ( s->map->gm_l = hit_crp_args ( s->hit_def, s->map->gm_h, &s->map->gm_f, corpus_arg, argv[i] ) ) <= 0 )
	{
	  strcpy ( s->errstr, BAD_CORPUS_ARGZ );
	  return BAD_ARGZ;
	}
      s->map->gm_eod = s->map->gm_l;
      /*
      fprintf (stderr, "corpus map: factor=%d, length=%d.\n", s->map->gm_f, s->map->gm_l); 
      fprintf (stderr, "first element on the corpus map: %d.\n", *s->map->gm_h); 
      */

    }

  /* finally, the output specs: */

  if ( output_arg )
    {
      if ( hit_out_args ( s->hit_def, output_arg ) )
	{
	  strcpy ( s->errstr, BAD_OUTPUT_ARGZ );
	  return BAD_ARGZ;
	}
    }
  else
    if ( hit_out_args ( s->hit_def, "binary" ) )
      {
	strcpy ( s->errstr, BAD_OUTPUT_ARGZ );
	return BAD_ARGZ;
      }



  return 0; 

}





