#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../plugin/hitcon.h"
#include "db.h"
#include "unpack.h"

int parsedbspecs(FILE *f) {
    int fields;
    int res;
    if (res = fscanf(f,"#define FIELDS %d", &fields)) {
        printf("%d fields.\n", fields);
    }
    else {
        printf("Couldn't get fields.\n");
        return 1;
    }
    return 0;
}

int main(int argc, char **argv) {

    char buffer[256];
    int form_ptr = 0;
    dbspec *dbs;
    dbh *db;
    char word[256];

	db = init_dbh_folder(argv[1]);

    int lu_type;
    int lu_freq;
    uint64_t lu_offset;
    int lu_blocks;
    int32_t *hits;

    while (fgets(buffer,256,stdin)) {
   		int i = 0;
   		int j = 0;
   		lu_type = 0;
   		lu_freq = 0;
   		lu_offset = 0;
   		lu_blocks = 0;
   		sscanf(buffer,"%s256",word);
   		fprintf(stderr,"looking up %s : ",word);
 		word_lookup(db,word);
		hits = hit_lookup(db,word,&lu_type,&lu_freq,&lu_blocks,&lu_offset);
		fprintf(stderr,"%d\n", lu_freq);
		if (lu_type == 0) {
			for (i = 0; i < (db->dbspec->fields * lu_freq); i++) {
				fprintf(stdout,"%d ",hits[i]);
			}
			fprintf(stdout,"\n");
	   	}
	   	else {
	   		fprintf(stderr, "%d blocks:\n", lu_blocks);
			int hit_offset = 0;
			int hit_offset_2;
			int32_t *temp_hit = malloc(sizeof(int32_t) * db->dbspec->fields);
			int32_t *block_hits;
			int block_count;
			int block_number = 0;
			for (i = 0; i < (db->dbspec->fields * lu_blocks); i++) {
				hit_offset = (i % db->dbspec->fields);
				temp_hit[hit_offset] = hits[i];
				if ((hit_offset == 8)) {
					fprintf(stdout,"\n");
					block_number++;
					block_hits = hit_gethits(db,lu_type,temp_hit,lu_offset,&block_count);
					hit_offset_2 = 0;
					for (j = 0; j < (db->dbspec->fields) * block_count; j++) {
						hit_offset_2 = (j % db->dbspec->fields);
						if (hit_offset_2 == 0) {
							fprintf(stdout,"\n");
						}
						fprintf(stdout,"%d ",block_hits[j]);
					}
					fprintf(stdout,"\n[%d hits in block %d]\n",block_count, block_number);
					lu_offset += db->dbspec->block_size;
				}
//				fprintf(stdout,"%d ",hits[i]);
			}
			fprintf(stdout,"\n");	   	
	   	
	   	
	   	}
    }
    return 0;
}
