#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "db.h"

dbh *init_dbh_folder(char *db_path) {
	
	dbh *db;
	dbspec *dbs;
    char *dbspecs_f; 
    char *dbm_f;
    char *block_f;
    FILE *dbspecs4;
    
    dbspecs_f = calloc(sizeof(char),256);
    dbm_f = calloc(sizeof(char),256);
    block_f = calloc(sizeof(char),256);
    
    strncat(dbspecs_f,db_path,192);
    strncat(dbspecs_f,"/src/dbspecs4.h", 64);
  
    strncat(dbm_f,db_path,192);
    strncat(dbm_f,"/index",64);
  
    strncat(block_f,db_path,192);
    strncat(block_f,"/index.1",64);
    
    dbspecs4 = fopen(dbspecs_f,"r");
    dbs = init_dbspec_file(dbspecs4);

    free(dbspecs_f);


    db = new_dbh(dbm_f,block_f, dbs);
    free(dbm_f);
    free(block_f);
    dbh_info(db);
    fclose(dbspecs4);
    return db;
}

dbspec *init_dbspec_file(FILE *dbspecs4) {
	char buffer[256];
	dbspec *dbs;
    int fields;
    int type_l;
    int blk_size;

    int freq1_l; 
    int freq2_l;
    int offst_l;

	if (dbspecs4 == NULL) {
        printf("bad dbspecs file.\n");
	    return NULL;
    }

    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer,"#define FIELDS %d", &fields)) {
            break;
        }
        return NULL;
    }
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define TYPE_LENGTH %d", &type_l)) {
            break;
        }
        return NULL;
    }
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer,"#define BLK_SIZE %d", &blk_size)) {
            break;
        }
        return NULL;
    }
  
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define FREQ1_LENGTH %d", &freq1_l)) {
            break;
        }
        return NULL;
    }
  
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define FREQ2_LENGTH %d", &freq2_l)) {
            break;
        }
        return NULL;
    }
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define OFFST_LENGTH %d", &offst_l)) {
            break;
        }
        return NULL;
    }
  
    int negs[fields];
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define NEGATIVES {%d,%d,%d,%d,%d,%d,%d,%d,%d", &negs[0],&negs[1],&negs[2],&negs[3],&negs[4],&negs[5],&negs[6],&negs[7],&negs[8])) {
            break;
        }
        return NULL;
    }
    int deps[fields];
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define DEPENDENCIES {%d,%d,%d,%d,%d,%d,%d,%d,%d", &deps[0],&deps[1],&deps[2],&deps[3],&deps[4],&deps[5],&deps[6],&deps[7],&deps[8])) {
            break;
        }
        return NULL;
    }
    int bits[fields];
    while (fgets(buffer,256,dbspecs4) != NULL) {
        if (sscanf(buffer, "#define BITLENGTHS {%d,%d,%d,%d,%d,%d,%d,%d,%d", &bits[0],&bits[1],&bits[2],&bits[3],&bits[4],&bits[5],&bits[6],&bits[7],&bits[8])) {
            break;
        }
        return NULL;
    }

    dbs = new_dbspec(fields, 
                     type_l,
                     blk_size,
                     freq1_l,
                     freq2_l,
                     offst_l,
                     negs,
                     deps,
                     bits);
	return dbs;
}

dbspec *new_dbspec(int fields, 
                   int type_length,
                   int block_size,
                   int freq1_length,
                   int freq2_length,
                   int offset_length,
                   int *negatives,
                   int *dependencies,
                   int *bitlengths)
    {
        int i;
        dbspec *dbs_ptr;        

        if ( (dbs_ptr = malloc(sizeof(dbspec) ) )== NULL) {
            printf("out of memory; dbspec allocation failed.");
            return dbs_ptr;
        }
        
        dbs_ptr->fields = fields;
        dbs_ptr->type_length = type_length;
        dbs_ptr->block_size = block_size;
        dbs_ptr->freq1_length = freq1_length;
        dbs_ptr->freq2_length = freq2_length;
        dbs_ptr->offset_length = offset_length;
        
        dbs_ptr->negatives = malloc(fields * sizeof(int));
        dbs_ptr->dependencies = malloc(fields * sizeof(int));
        dbs_ptr->bitlengths = malloc(fields * sizeof(int));
        
	dbs_ptr->bitwidth = 0;
	
        for ( i = 0; i < fields; i++) {
            dbs_ptr->negatives[i] = negatives[i];
            dbs_ptr->dependencies[i] = dependencies[i];
            dbs_ptr->bitlengths[i] = bitlengths[i];
            dbs_ptr->bitwidth += bitlengths[i];
        }
            
        dbs_ptr->hits_per_block = (dbs_ptr->block_size * 8) / dbs_ptr->bitwidth;
        dbs_ptr->uncompressed_hit_size = sizeof(uint32_t) * dbs_ptr->fields;
        
        return dbs_ptr;         
    }

int delete_dbspec(dbspec *dbs) {
  free(dbs->negatives);
  free(dbs->dependencies);
  free(dbs->bitlengths);
  free(dbs);
  return 0;
}

int delete_dbh(dbh *db) {
  delete_dbspec(db->dbspec);
  gdbm_close(db->hash_file);
  fclose(db->block_file);
  free(db);
  return 0;
}

dbh *new_dbh(char *gdbm_f, char *block_f, dbspec *dbs) {
	dbh *dbh_ptr;
	dbh_ptr = malloc(sizeof(dbh));

	dbh_ptr->hash_file = gdbm_open(gdbm_f,0,GDBM_READER, 0, 0);
	if (dbh_ptr->hash_file == NULL) {
		printf("error opening hash table at %s.\n", gdbm_f);
		exit(1);
	}

	dbh_ptr->block_file = fopen(block_f,"r");
	if (dbh_ptr->block_file == NULL) {
		printf("error opening block file at %s.\n", block_f);
		exit(1);
	}

	dbh_ptr->dbspec = dbs;
	
	return dbh_ptr;		
}

int dbh_info(dbh *db) {
	fprintf(stderr,"fields: %d\n",db->dbspec->fields);
	fprintf(stderr,"type_length: %d\n",db->dbspec->type_length);
	fprintf(stderr,"block_size: %d\n",db->dbspec->block_size);
	fprintf(stderr,"freq1_length: %d\n",db->dbspec->freq1_length);
	fprintf(stderr,"freq2_length: %d\n",db->dbspec->freq2_length);
	fprintf(stderr,"offset_length: %d\n",db->dbspec->offset_length);
	fprintf(stderr,"negatives: (%d,%d,%d,%d,%d,%d,%d,%d,%d)\n",db->dbspec->negatives[0],db->dbspec->negatives[1],db->dbspec->negatives[2],db->dbspec->negatives[3],db->dbspec->negatives[4],db->dbspec->negatives[5],db->dbspec->negatives[6],db->dbspec->negatives[7],db->dbspec->negatives[8]);
	fprintf(stderr,"dependencies: (%d,%d,%d,%d,%d,%d,%d,%d,%d)\n",db->dbspec->dependencies[0],db->dbspec->dependencies[1],db->dbspec->dependencies[2],db->dbspec->dependencies[3],db->dbspec->dependencies[4],db->dbspec->dependencies[5],db->dbspec->dependencies[6],db->dbspec->dependencies[7],db->dbspec->dependencies[8]);
	fprintf(stderr,"bitlengths: (%d,%d,%d,%d,%d,%d,%d,%d,%d)\n",db->dbspec->bitlengths[0],db->dbspec->bitlengths[1],db->dbspec->bitlengths[2],db->dbspec->bitlengths[3],db->dbspec->bitlengths[4],db->dbspec->bitlengths[5],db->dbspec->bitlengths[6],db->dbspec->bitlengths[7],db->dbspec->bitlengths[8]);
	return 0;
}
