#include "unpack.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

int word_lookup(dbh *db, Z8 *keyword) {

	int freq = 0;
	int type;
	int offset;
	int pos, len;
	int blocks;
	
	bitsvector *v;
	datum key,val;

	key.dptr = keyword;
	key.dsize = strlen(keyword);

	val = gdbm_fetch(db->hash_file,key);

	if (val.dptr == NULL) {
		return 0;
	}	

	v = bitsvectorNew((N8 *) val.dptr);

	len = val.dsize << 3;	
	type = bitsvectorGet(v,db->dbspec->type_length);

	fprintf(stderr, "%s is a word of type %d, ",keyword, type);

	if (type == 0) {
		freq = bitsvectorGet(v,db->dbspec->freq1_length);		
		offset = 0;
		pos = bitsvectorTell(v);
		blocks = 0;
	}
	else {
		freq = bitsvectorGet(v,db->dbspec->freq2_length);
		offset = bitsvectorGet(v,db->dbspec->offset_length);
		pos = bitsvectorTell(v);
		blocks = (len - pos) / (db->dbspec->bitwidth);
	}

	fprintf(stderr, "%d occurrences.  vector is %d bits long, each hit is %d bits wide.\n", freq, len,db->dbspec->bitwidth);
	fprintf(stderr, "at bit position %d, blocks start at %d, so there must be %d blocks total.\n",pos, offset, blocks);
	return freq;
}

Z32 *hit_lookup(dbh *db, Z8 *keyword, N32 *type_num, N32 *freq, N32 *blkcount, N64 *offset) {
	int pos, len;
	Z32 *ret;
	bitsvector *v;
	datum key,val;

	key.dptr = keyword;
	key.dsize = strlen(keyword);

	val = gdbm_fetch(db->hash_file,key);

	if (val.dptr == NULL) {
		*freq = 0;
		return NULL;
	}

	v = bitsvectorNew((N8 *) val.dptr);

	len = val.dsize << 3;	
	*type_num = bitsvectorGet(v,db->dbspec->type_length);

	if (*type_num == 0) {
		*freq = bitsvectorGet(v,db->dbspec->freq1_length);
		*offset = 0;
		pos = bitsvectorTell(v);
		*blkcount = 0;
		ret = unpack(db,v,*freq);
		bitsvectorOld(v);
		return ret;
	}
	else {
		*freq = bitsvectorGet(v,db->dbspec->freq2_length);
		*offset = bitsvectorGet(v,db->dbspec->offset_length);
		pos = bitsvectorTell(v);
		*blkcount = (len - pos) / (db->dbspec->bitwidth);
		ret = unpack(db,v,*blkcount);
		bitsvectorOld(v);
		return ret;;
	}
}

int32_t *unpack(dbh *db, bitsvector *v, N32 count) {
	int i;
	int j;
	int k = 0;
	int32_t *hits = malloc(sizeof(int32_t)*(db->dbspec->fields)*count);
	if (hits == NULL) {
		fprintf(stderr, "out of memory error: couldn't decompress hits.\n");
		exit(1);
	}

	for (i = 0; i < count; i++) {
		for (j = 0; j < db->dbspec->fields; j++) {
			hits[k] = bitsvectorGet(v,db->dbspec->bitlengths[j]) - db->dbspec->negatives[j];
			k += 1;
		}
	}

	return hits;	
}

int32_t *hit_gethits(dbh *db, N32 type, Z32 *first, N64 offset, N32 *blockcount) {
	N8 *buffer = malloc(sizeof(Z8) * db->dbspec->block_size);
	bitsvector *v;
	int32_t *hits;
	int32_t *temp = malloc(sizeof(N32)*db->dbspec->fields);
	int i;
	int block_end = 0;
	int hit_counter = 0;
	int res;

	if ( fseeko (db->block_file, offset, 0) ){
    	fprintf(stderr,"improper seek!\n");
	}
	res = fread (buffer, sizeof(N8), db->dbspec->block_size, db->block_file);
	v = bitsvectorNew(buffer);
	
	//allocate enough space for a block plus a header.  ugly expression.
	hits = malloc(sizeof(N32)*db->dbspec->fields*( 1 + (db->dbspec->block_size << 3) / db->dbspec->bitwidth));
	
	//the header is the first hit on the vector
	for (i = 0; i < db->dbspec->fields; i++) {
		hits[i] = first[i];	
		
	}
	hit_counter = 1;
	while (!block_end) {
		for (i = 0; i < db->dbspec->fields; i++) {
			temp[i] = bitsvectorGet(v,db->dbspec->bitlengths[i]);
		}
		block_end = 1;
		// if we might still be in a block :
		if ( bitsvectorTell ( v ) <= db->dbspec->block_size << 3 ) {
			//look for the flag of all binary 1's for the width of a hit.
			for (i = 0; i < db->dbspec->fields; i++) {
				//otherwise
				if (temp[i] != (( 1 << db->dbspec->bitlengths[i] ) - 1 )) {
					//the hit is good.
					block_end = 0;
				}
			}
			//in which case we can copy it onto the results.
			if (!block_end) {
				for (i = 0; i < db->dbspec->fields; i++) {
					hits[(db->dbspec->fields * hit_counter)+i] = temp[i] - db->dbspec->negatives[i];
				}
				//and add to our tally.
				hit_counter++;
			}
		}
	}
	bitsvectorOld(v);
	free(temp);
	*blockcount = hit_counter;
	return hits;
}
