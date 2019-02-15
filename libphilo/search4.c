#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include "c.h"
#include "search.h"

int main(int argc, char **argv) {

	int c;
	int option_index;
	int remaining_argument = 0;
	int argcounter = 1;

	char method[256];
	int method_set = 0;
	char dbname[256];
	int dbname_set = 0;
	char search_arg[256];
	int arg_set = 0;
	char *temp_search_arg = NULL;

	int ascii_set = 0;
	int corpussize = 1;
	char corpusfile[256];
	int corpusfile_set = 0;
	int debug = 0;
	int limit = 0;

	Search s;
	dbh *db;
	int status;

	char *usage = "search4 [--ascii --corpussize c --corpusfile f --debug d --limit l] dbname [search method]\n";

	static struct option long_options[] =
		{
			{"ascii", no_argument, 0, 'a'},
			{"corpussize", required_argument, 0, 'c'},
			{"corpusfile", required_argument, 0, 'f'},
			{"debug", required_argument, 0, 'd'},
			{"limit", required_argument, 0, 'l'},
			{0,0,0,0}
		};

	while (0 < (c = getopt_long(argc, argv, "ac:d:f:l:", long_options, &option_index) ) ) {
		//while we step through all options in argv:
		fprintf(stderr,"%s is set. ", long_options[option_index].name);
		if (optarg) {
			fprintf (stderr," with arg %s", optarg);
		}
		switch(c) {
			case 'a':
				ascii_set = 1;
				break;
			case 'l':
				limit = atol(optarg);
				break;
			case 'c':
				corpussize = atoi(optarg);
				break;
			case 'f':
				strncpy(corpusfile,optarg,255);
				corpusfile_set = 1;
			default:
				break;
		}
		fprintf(stderr,"\n");
	}

	if (!corpusfile_set) {
		corpussize = 0;
	}

	while (optind < argc) {
		if (argcounter == 1) {
			strncpy(dbname, argv[optind],256);
			// fprintf(stderr,"database name is %s\n",dbname);
			dbname_set = 1;
		}
		if (argcounter == 2) {
			strncpy(method, argv[optind],256);
			// printf("search method is %s\n",method);
			method_set = 1;
		}
		if (argcounter == 3) {
			strncpy(search_arg, argv[optind], 256);
		  	// printf("search arg is %s\n",search_arg);
		  	arg_set = 1;
		}
		optind += 1;
		argcounter += 1;
	}

	if (!dbname_set) {
		printf("%s", usage);
		return 1;
	}

	db = init_dbh_folder(dbname);
	if (!method_set) {
		strncpy(method,"phrase",256);
	}
	if (arg_set) {
	  temp_search_arg = malloc(sizeof(Z8 *) * 256);
	  strncpy(temp_search_arg,search_arg,256);
	}
	s = new_search(db, method, temp_search_arg, ascii_set,limit,corpussize,corpusfile);
	status = process_input ( s, stdin );
	if ( status == BATCH_EMPTY ) {
		fprintf(stderr,"no hits found.\n");
		return 0;
	}
	//	s->batches->map = s->map;
	while ( (status = search_pass ( s, 0 )) == SEARCH_PASS_OK ) {
		continue;
	}
	delete_search(s);
	delete_dbh(db);
	return 0;
}
