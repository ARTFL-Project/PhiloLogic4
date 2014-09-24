// $Id: args.h,v 2.11 2004/05/28 19:22:06 o Exp $
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


#ifndef C_H
  #include "c.h"
#endif

#define BAD_ARGZ                1

#define BAD_ENGINE_ARGZ         "badly defined output (-E:) arguments"
#define BAD_SEARCH_ARGZ         "badly defined search (-S:) arguments"
#define BAD_CORPUS_ARGZ         "badly defined corpus (-C:) arguments"
#define BAD_OUTPUT_ARGZ         "badly defined output (-P:) arguments"
#define BAD_PLUGIN_ARGZ         "badly defined plugin (-D:) argument"


extern Z32 process_command_argz(); 
extern Z32 process_command_argz_backwardcompat(); 


