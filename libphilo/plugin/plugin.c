// $Id: plugin.c,v 2.11 2004/05/28 19:22:08 o Exp $
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

#include "plugin.h"
#include <stdlib.h>
dbPlugin artfl =
{
  new_hitdef,
  get_plugin_info_artfl
};

struct 
{
  Z8      *dbp_tag;
  dbPlugin  *dbp;
} 
dbPlugins[] = 
{
  { (Z8 *)"artfl2t", &artfl },
  { 0, 0 }
};                                                                             

Z8 *get_plugin_info_artfl ()
{
  Z8 *ret;

  ret = malloc ( 256* sizeof(Z8) ); 
  sprintf ( (char *)ret, "This is the builtin (default) plugin for ARTFL textual database v.2t" );

  return ret; 
}

