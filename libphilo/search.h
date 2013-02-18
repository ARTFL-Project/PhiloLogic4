// $Id: search.h,v 2.11 2004/05/28 19:22:06 o Exp $
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


#ifdef SEARCH_H
  #error "search.h multiply included"
#else
  #define SEARCH_H
	#include "db/db.h"
  #ifndef C_H
    #include "c.h"
  #endif 

  #define  MAP_INIT_LEN  8192

  #define DEFAULT_BATCH_LIMIT   8192
  #define DEFAULT_PRINT_LIMIT   3000

  #define SEARCH_PASS_OK               0
  #define SEARCH_BUMMER_OCCURED        1
  #define SEARCH_PASS_FINISHED         2
  #define SEARCH_BATCH_FINISHED        3
  #define SEARCH_BATCH_LIMIT_REACHED   4
  #define SEARCH_PRINT_LIMIT_REACHED   5

#define BAD_ARGZ                1

#define BAD_ENGINE_ARGZ         "badly defined output (-E:) arguments"
#define BAD_SEARCH_ARGZ         "badly defined search (-S:) arguments"
#define BAD_CORPUS_ARGZ         "badly defined corpus (-C:) arguments"
#define BAD_OUTPUT_ARGZ         "badly defined output (-P:) arguments"
#define BAD_PLUGIN_ARGZ         "badly defined plugin (-D:) argument"
  typedef struct Search *Search, Search_; 

  #ifndef BATCH_H
    #include "level.h"
  #endif

  #ifndef HIT_H
    #include "plugin/hit.h"
  #endif

  #ifndef LOG_H
    #include "log.h"
  #endif

  struct Search
  {
  	dbh *db;
    N32   depth;
    N32   depth_r;
    Batch batches;

    hitdef *hit_def;


    Z32    bn;
    
    Z32    bincorpus;
    Z8     *corpus;
    N8     cfactor;

    Gmap   map;

    Z32    debug; 

    Z32    print_limit; 
    Z32    n_printed;
    Z32    batch_limit; 
/*    Z32    offset; */
    Z32    soft_limit; 

    Z32    exitcode;
    Z8     errstr[1024];

  };

  extern Search new_searchObject ();
Search new_search( dbh *db, Z8 *method, Z8 *arg, int ascii, int limit, int corpussize, char * corpusfile);
int set_search_method( Search s, Z8 *methodstring, Z8 *argstring);
#endif







