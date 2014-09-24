// $Id: method.c,v 2.11 2004/05/28 19:22:08 o Exp $
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

#include "method.h"

SearchMethod cooc =
{
  build_search_level_cooc,
  get_method_info_cooc
};


SearchMethod phrase =
{
  build_search_level_phrase,
  get_method_info_phrase
};


SearchMethod proxy =
{
  build_search_level_proxy,
  get_method_info_proxy
};

SearchMethod sentence = 
{
  build_search_level_sentence,
  get_method_info_sentence
};

SearchMethodEntry SearchMethods[] = 
{
  { (Z8 *)"cooc", &cooc },
  { (Z8 *)"phrase", &phrase },
  { (Z8 *)"proxy", &proxy },
  { (Z8 *)"sentence", &sentence },
  { 0, 0 }
};                                                                             


