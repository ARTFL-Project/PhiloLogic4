#ifndef _INC_DB_H
#define _INC_DB_H

#include <gdbm.h>
#include <stdio.h>
#include <stdint.h>

struct philo_dbspec
       {
           int fields;
           int type_length;
           int block_size;
           int freq1_length;
           int freq2_length;
           int offset_length;
           int *negatives;
           int *dependencies;
           int *bitlengths;
           int bitwidth;
           int hits_per_block;
           int uncompressed_hit_size;
       };

typedef struct philo_dbspec dbspec;

dbspec *new_dbspec(int fields, 
           		   int type_length,
           	       int block_size,
                   int freq1_length,
                   int freq2_length,
                   int offset_length,
                   int *negatives,
                   int *dependencies,
                   int *bitlengths);

int delete_dbspec(dbspec* dbs_ptr);

dbspec *init_dbspec_file(FILE *dbspec);

struct philo_dbh
	{
		   GDBM_FILE hash_file;
		   FILE *block_file;
		   dbspec *dbspec;
	};
	
typedef struct philo_dbh dbh;

dbh *new_dbh(char *gdbm_f, char *index_f, dbspec *dbs);
dbh *init_dbh_folder(char *db_path);
int delete_dbh(dbh *dbh_ptr);
int dbh_info(dbh *db);
#endif 
