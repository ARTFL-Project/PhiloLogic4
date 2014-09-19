#include "pack.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

int main(int argc, char **argv) {
// main() should probably be in a separate file, and pack.c should get linked into libphilo.  

	char testword = 0;
	FILE *dbspecs4;
	dbspec *dbs = NULL;
	hitbuffer *hb = NULL;

	N64 totalhits = 0;
	N64 wordhits = 0;
	N64 uniq_words = 0;
	char word[512];
	char page[512];
	char line[512];
	int state;
	Z32 hit[10];

	//hack for pages
	hit[8] = 0;

	if (argc < 2) {
		exit(1);
	}
	
	//load dbspecs.
	fprintf(stderr, "reading dbspecs in from %s...\n", argv[1]);
	dbspecs4 = fopen(argv[1],"r");
	if (dbspecs4 == NULL) {
		fprintf(stderr, "couldn't open %s for reading.\n", argv[1]);
		exit(1);
	}
	dbs = init_dbspec_file(dbspecs4);
	if (dbs == NULL) {
		fprintf(stderr, "couldn't understand %s.\n", argv[1]);
		exit(1);
	}
	
	//create the hitbuffer object.
	hb = new_hb(dbs);

	//scanning
	while(1) {
		if (fgets(line,511,stdin) == NULL) {
			hitbuffer_finish(hb);
			break;		
		}
		state = sscanf(line,
		               "word\t%s\t%d %d %d %d %d %d %d %d %d", 
		               word, &hit[0],&hit[1],&hit[2],&hit[3],&hit[4],&hit[5],&hit[6],&hit[7], &hit[8]
					  );

		if (state == 10) {
			if ((strcmp(word,hb->word))) {
			//if we have a new word...
				hitbuffer_finish(hb); // write out the current buffer.
				hitbuffer_init(hb, word); // and reinitialize
				uniq_words += 1LLU; //LLU for a 64-bit unsigned int.
			}
			hitbuffer_inc(hb, hit); //then add the hit to whichever word you're on.
			totalhits += 1LLU;
		}
		else {
			fprintf(stderr, "Couldn't understand hit.\n");
		}
	}

	fprintf(stderr, "done. %d hits packed in %d entries.\n", (int)(totalhits), (int)(uniq_words));
	delete_hb(hb);
	delete_dbspec(dbs);
	return 0;
}

hitbuffer *new_hb(dbspec *dbs) {
	GDBM_FILE gdbh;
	FILE *blocks;
	hitbuffer *hb = NULL;
	
	//initialize gdbm.
	gdbh = gdbm_open("index",0,GDBM_NEWDB, 0666,0);
	if (gdbh == NULL) {
		fprintf(stderr, "couldn't create index\n");
		exit(2);
	}
	
	//open the block file
	blocks = fopen("index.1","wb");
	if (blocks == NULL) {
		fprintf(stderr, "couldn't create index.1\n");
		exit(3);
	}
	
	//ugly...
	hb = malloc(sizeof(hitbuffer));
	hb->db = malloc(sizeof(dbh));

	hb->db->hash_file = gdbh;
	hb->db->block_file = blocks;
	hb->db->dbspec = dbs;
	strcpy(hb->word, "");

	// the dir can grow dynamically.  start it small.
	hb->dir = malloc(hb->db->dbspec->block_size);
	hb->dir_malloced = hb->db->dbspec->block_size;

	// the block should not grow, since it has a fixed upper size, which we can calculate.
	hb->blk = malloc(hb->db->dbspec->uncompressed_hit_size * hb->db->dbspec->hits_per_block); 
	hb->blk_malloced = hb->db->dbspec->uncompressed_hit_size * hb->db->dbspec->hits_per_block;

	hb->offset = 0;

	return hb;
}

int delete_hb(hitbuffer *hb) {
	free(hb->dir);
	free(hb->blk);
	gdbm_close(hb->db->hash_file);
	fclose(hb->db->block_file);
	free(hb->db);
	free(hb);
	return 0;
}

int hitbuffer_init(hitbuffer *hb, Z8 *word) {
	strncpy(hb->word,word,strlen(word) + 1);
	hb->type = 0;
	hb->freq = 0;
	hb->in_block = 0;
	hb->dir_length = 0;
	hb->blk_length = 0;
	hb->offset = ftell(hb->db->block_file);
	return 0;
}

int hitbuffer_inc(hitbuffer *hb, Z32 *hit) {
	hb->freq += 1LLU; //LLU for 64-bit.  OSX 10.5 is VERY finicky about this.
	int result;
	if (hb->freq < PHILO_INDEX_CUTOFF) {
		add_to_dir(hb, hit, 1);
//		fprintf(stderr, "added hit for %s...\n", hb->word);
	}
	else if (hb->freq == PHILO_INDEX_CUTOFF) {
			//when the frequency reaches 10, we start using a block-header layout.
			//each "hit" in the directory corresponds to a large, compressed block of hits.
			//by comparing the directory headers to the query, the search engine skips blocks if possible.

			result = add_to_block(hb,&(hb->dir[1*hb->db->dbspec->fields]),PHILO_INDEX_CUTOFF - 2);
			if (result == PHILO_BLOCK_FULL) {
				fprintf(stderr, "you can't fit PHILO_INDEX_CUTOFF hits into a block!  adjust your block size, or your index cutoff.\n");	
			}

			hb->dir_length = 1LLU;
			hb->type = 1;
			result = add_to_block(hb,hit,1);
//			fprintf(stderr, "clearing dir.  started new block for %s...\n", hb->word);
	}
	if (hb->freq > PHILO_INDEX_CUTOFF) {
		result = add_to_block(hb,hit,1);
		if (result == PHILO_BLOCK_FULL) {
			// IF the block add failed,
			write_blk(hb); //write the full block out, start a new one,
			add_to_dir(hb,hit,1); //then push the current hit onto the directory.
//			fprintf(stderr, "started new block for %s...\n", hb->word);
		}
	}		
	return 0;
}

int hitbuffer_finish(hitbuffer *hb) {
	if (!strcmp(hb->word, "")) {
		return 0;
	}
	if (hb->type == 0) {	
	  //		fprintf(stderr, "%s: %d\n", hb->word, (int)hb->freq);
		write_dir(hb);
	}
	else if (hb->type == 1) {
	  //	fprintf(stderr, "%s: %d [%d blocks]\n", hb->word, (int)hb->freq, (int)hb->dir_length);
		write_dir(hb);
		write_blk(hb);
	}
	return 0;
}

int add_to_dir(hitbuffer *hb, Z32 *data, N32 count) {
	//there is no fixed upper limit to directory size, so the dir structure has to grow dynamically.
	//this doesn't happend for each hit.  the dir object isn't freed until the program terminates.
	void *status;
	while (hb->dir_malloced < ((hb->dir_length + count) * (hb->db->dbspec->fields) * sizeof(Z32)) ) {
		hb->dir = realloc(hb->dir, 2 * hb->dir_malloced);
		if (hb->dir) {
			hb->dir_malloced = 2 * hb->dir_malloced; //I'm trying to save time from calling malloc over and over again, but is this too aggressive?
		}
		else {
			fprintf(stderr, "out of memory: couldn't add hit to directory.  \nconsider using disk for index state, or adjusting the realloc amount.\n");
			exit(1);
		}
	}
	memcpy(&hb->dir[hb->dir_length * (hb->db->dbspec->fields)], //the address of the new hits
		   data, //the data buffer
	       count * (hb->db->dbspec->fields) * sizeof(Z32) //the size of the data buffer
	      );
	hb->dir_length += (N64)(count);
	return 0;
}

int add_to_block(hitbuffer *hb, Z32 *data, N32 count) {
	//a block has a fixed size in bytes, but that applies AFTER compression.
	//I calculate the number of hits per block, based on hit width and block size,
	//when I parse the dbspecs.  
	
	int i,j;
	
	N64 hits_per_block = (hb->db->dbspec->block_size * 8)  / (hb->db->dbspec->bitwidth);
	N64 free_space = hits_per_block - hb->blk_length;

	if (count <= free_space ) { //
		//if there's room, copy the hits over.
		memmove(&hb->blk[hb->blk_length * (hb->db->dbspec->fields)] ,
			   data,
			   count * hb->db->dbspec->fields * sizeof(Z32)
			  );

		hb->blk_length += count;
		return 0; 
	}
	else {
		//the block is full, or full enough.
		return PHILO_BLOCK_FULL;
	}
}

int write_dir(hitbuffer *hb) {
	int header_size;
	int buffer_size;
	int offset = 0;
	int bit_offset = 0;
	
	datum key, value;
	
	int i;
	int j;
	
	const dbspec *dbs = hb->db->dbspec;
	char *valbuffer;
	
	if (hb->type == 0) {
		header_size = dbs->type_length + dbs->freq1_length;
	}
	else {
		header_size = dbs->type_length + dbs->freq2_length + dbs->offset_length;
	}
	
	buffer_size = ( (header_size + (hb->dir_length * dbs->bitwidth)  ) / 8) + 1;
	valbuffer = calloc(buffer_size + 1, sizeof(char));
	
	if (valbuffer == NULL) {
		//should add helpful error here.
		exit(1);
	}

	//Compress..we'll see this idiom a lot.  arguably I should just take a bit offset for simplicity.
	compress(valbuffer,offset,bit_offset,(N64)hb->type,dbs->type_length);
	offset += dbs->type_length / 8;
	bit_offset += dbs->type_length % 8;
	
	//Low frequency words just have frequency in the header
	if (hb->type == 0) {
		compress(valbuffer,offset,bit_offset,(N64)hb->freq,dbs->freq1_length);
		offset += (bit_offset + dbs->freq1_length) / 8;
		bit_offset = (bit_offset + dbs->freq1_length) % 8;
	}

	//High frequency words have byte offset of the block tree as well.
	else if (hb->type == 1) {
		compress(valbuffer,offset,bit_offset,(N64)hb->freq,dbs->freq2_length);
		offset += (bit_offset + dbs->freq2_length) / 8;
		bit_offset = (bit_offset + dbs->freq2_length) % 8;
		
		compress(valbuffer,offset,bit_offset,(N64)hb->offset,dbs->offset_length);
		offset += (bit_offset + dbs->offset_length) / 8;
		bit_offset = (bit_offset + dbs->offset_length) % 8;
	}
	
	//compress the hits themselves.
	for (i = 0; i < hb->dir_length; i++) {
		for (j = 0; j < dbs->fields; j++) {
			compress(valbuffer,offset,bit_offset,(N64)(hb->dir[i*dbs->fields + j] + dbs->negatives[j]), dbs->bitlengths[j]);
			offset += (bit_offset + dbs->bitlengths[j]) / 8;
			bit_offset = (bit_offset + dbs->bitlengths[j]) % 8;
		}
	}

	//Write to GDBM
	
	key.dptr = hb->word;
	key.dsize = strlen(hb->word);
	value.dptr = valbuffer;
	value.dsize = buffer_size;
	gdbm_store(hb->db->hash_file, key, value,GDBM_REPLACE);

	free(valbuffer);
	return 0;
}

int write_blk(hitbuffer *hb) {
	int offset = 0;
	int bit_offset = 0;
	int i,j;
	dbspec *dbs = hb->db->dbspec;
	int write_size;
	char *valbuffer = calloc(hb->db->dbspec->block_size, sizeof(char));

	//Compress 
	for (i = 0; i < hb->blk_length; i++) {
		for (j = 0; j < dbs->fields; j++) {
			compress(valbuffer,offset,bit_offset,(N64)(hb->blk[i*dbs->fields + j] + dbs->negatives[j]), dbs->bitlengths[j]);
			offset += (bit_offset + dbs->bitlengths[j]) / 8;
			bit_offset = (bit_offset + dbs->bitlengths[j]) % 8;			
		}
	}

	//Don't forget the block-end flag iff a block ends prematurely.
	if (hb->blk_length < dbs->hits_per_block) {
		for (j = 0; j < dbs->fields; j++) {
			compress(valbuffer,offset,bit_offset,(N64)((1LLU << dbs->bitlengths[j]) - 1), dbs->bitlengths[j]);
			offset += (bit_offset + dbs->bitlengths[j]) / 8;
			bit_offset = (bit_offset + dbs->bitlengths[j]) % 8;	
		}	
	}

	if (bit_offset) {
		offset = offset + 1; //iff we have a bit offset; blocks are byte-aligned, of course.
	}

	write_size = dbs->block_size;
	if (hb->blk_length < dbs->hits_per_block) {
		write_size = offset; //this actually saves a lot of space in a large database.
	}
	fwrite(valbuffer,sizeof(char),write_size,hb->db->block_file);
	
	hb->blk_length = 0;
	free(valbuffer);
	return 0;
}

int compress(char *bytebuffer, int byte, int bit, N64 data, int size) {
// ALWAYS remember to cast 'data' when you CALL compress().  
// the default conversion of int to uint64 is very bad.
	int free_space = 8 - bit;
	int remaining = size;
	char mask;
	int r_shift = 0; // we keep shifting data to the right as we write bits out.
	int to_do; // the number of bits to write in each pass.
	
	while (remaining > 0) { // as long as we still have bits to write
		if (free_space == 0) { // if there are no bits left in the current word
			byte += 1;		   // move on to the next one.
			free_space = 8;
		}

		to_do = (remaining >= free_space) ? free_space : remaining;

		data >>= r_shift; //trim off what we've done already.
		mask = (1 << to_do) - 1; //this will mask out high bits, leaving only 'to_do' low order bits.
		bytebuffer[byte] |= ((char)data & mask) << (8-free_space); //mask, then shift into place.
		
		remaining -= to_do;
		free_space -= to_do;
		r_shift = to_do;
	}
	return 0;	
}
