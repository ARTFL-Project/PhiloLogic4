#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "db.h"
#include "unpack.h"

typedef struct word_rec {
  char *word;
  int type;
  uint64_t freq;
  int block_count;
  int current_block;
  int block_position;
  int header_position;
  uint64_t start_offset;
  uint32_t *header_hits;
  bitsvector *header;
  bitsvector *block;
  uint32_t *current_hit;
  uint32_t *next_header;
} word_rec;

typedef struct word_heap {
  dbh *db;
  word_rec *records;
  size_t rec_count;
  size_t rec_alloced;
  void * cmp;
  uint32_t *hit_buffer;
  size_t hit_count;
  size_t hit_alloced;
} word_heap;

word_rec fetch_word(dbh *db, char *word) {
  word_rec rec;
  datum key,val;
  int len,pos,block_size,header_hits;

  rec.word = malloc(strlen(word));
  strcpy(rec.word,word);

  key.dptr = word;
  key.dsize = strlen(word);

  val = gdbm_fetch(db->hash_file,key);
  if (val.dptr == NULL) {
    //    return 0; ?? probably need to make this a pointer type and return null.
  }
  len = val.dsize << 3; // size of the vector in bits

  rec.header = bitsvectorNew((char *)val.dptr);
  rec.block = NULL;
  rec.type = bitsvectorGet(rec.header,db->dbspec->type_length);
  if (rec.type == 0) {
    rec.freq = bitsvectorGet(rec.header,db->dbspec->freq1_length);
    rec.start_offset = 0;
  } else {
    rec.freq = bitsvectorGet(rec.header,db->dbspec->freq2_length);
    rec.start_offset = bitsvectorGet(rec.header,db->dbspec->offset_length);
  }

  pos = bitsvectorTell(rec.header);
  header_hits = (len - pos) / (db->dbspec->bitwidth);
  fprintf(stderr,"%s at bit %d of %d; %d hits remaining in header.\n",rec.word,pos,len,header_hits);
  if (rec.type == 1) {
    rec.block_count = header_hits; 
  } else { 
    rec.block_count = 0;
  }
  
  rec.current_block = 0;
  rec.block_position = 0; // position 0 means the header is the next hit, and the block hasn't been fetched yet.
  rec.current_hit = calloc(1,db->dbspec->fields * sizeof(uint32_t));
  return rec;
}

void read_hit(dbh *db, bitsvector *v, uint32_t *hits) {
  int i;
  for (i = 0; i < db->dbspec->bitlengths[i]; i++) {
    hits[i] = bitsvectorGet(v,db->dbspec->bitlengths[i]);
  }
}

uint32_t *word_next_hit(dbh *db, word_rec *rec) {
  bitsvector *peek;
  int res,i;
  char *buffer;
  uint32_t *temp_hit;

  if (rec->type == 0) {
    if (rec->header_position < rec->freq) { 
      read_hit(db,rec->header,rec->current_hit);
      rec->header_position += 1;
      return rec->current_hit;
    }
    else {
      return NULL;
    }

  } else if (rec->type == 1) {   
    if (rec->header_position < rec->block_count) { // if we aren't past the last block
      if (rec->block_position == 0) { // if we need to start a new block...

	// read the header.
	read_hit(db,rec->header,rec->current_hit); 
	rec->header_position += 1;
	rec->block_position += 1; // note that we haven't actually read from a block, or loaded it

	// free the old block vector
	if (rec->block != NULL) {
	  bitsvectorOld(rec->block);
	  rec->block = NULL;
	}

	// peek at the next header hit, if we're not on the last block
	if (rec->header_position < rec->block_count) {
	  peek = rec->header; // save the state of the header vector
	  read_hit(db,rec->header,rec->next_header); // read the next block
	  rec->header = peek; // rewind
	} else { // if we're on the last block
	  rec->next_header = NULL;
	}
	return rec->current_hit;
      }
      else { // if we've read the header of the current block..

	// we may still need to load it from disk.
	if (rec->block_position = 1) {
	  buffer = malloc(sizeof(char) * db->dbspec->block_size);
	  res = fread(buffer,sizeof(char),db->dbspec->block_size, db->block_file);
	  rec->block = bitsvectorNew(buffer);	
	} 
	// once it's loaded, read it into a temp buffer.
	temp_hit = malloc(db->dbspec->fields * sizeof(uint32_t));
	read_hit(db,rec->block,temp_hit);
	// a hit consisting of all binary 1's is actually an end-of-block flag
	for (i = 0; i < db->dbspec->fields; i++) {
	  if (temp_hit[i] != (( 1 << db->dbspec->bitlengths[i] ) - 1 )) {
	    // the hit is good, return it.
	    rec->block_position += 1;
	    rec->current_hit = temp_hit;
	    return rec->current_hit;
	  }
	}
	// the hit is fake, we need to go to the next block.
	rec->block_count += 1;
	rec->block_position = 0;
	// call ourselves recursively, we can check there if we've gone off the last block.
	return word_next_hit(db,rec);
      }
    }
    else { // if we're off the end of the block list      
      return NULL;
    }
  }
}

word_rec new_word_rec(dbh *db, char *word) {
  word_rec rec;

  rec.header_hits = hit_lookup(db,
			       word,
			       &rec.type,
			       (uint32_t *)&rec.freq, /*fix this*/
			       &rec.block_count,
			       &rec.start_offset);
  rec.word = malloc(strlen(word));
  strcpy(rec.word,word);
  
  rec.current_block = 0;
  
  return rec;
}

word_heap new_heap(dbh * db) {
  word_heap heap;
  heap.db = db;
  heap.records = NULL;
  heap.rec_count = 0;
  heap.rec_alloced = 0;
  heap.cmp = NULL;
  heap.hit_buffer = NULL;
  heap.hit_count = 0;
  heap.hit_alloced = 0;
  return heap;
}

void start_stream(word_heap *heap) {
  int i;
  for (i = 0; i < heap->rec_count; i++) {
    if (heap->records[i].type == 0) {
      fprintf(stdout,"dumping header for %s\n",heap->records[i].word);
    } else {
      fprintf(stdout,"dumping block 1 for %s\n",heap->records[i].word); 
    }
  }
}

void add_record(word_heap *heap, word_rec *rec) {
  /* first make space if needed */
  if (heap->rec_count <= heap->rec_alloced) {
    /* should check for success here; running out of memory is a real concern */
    heap->records = realloc(heap->records,sizeof(word_rec)*(heap->rec_count+1) );
    /* should also consider expanding by a larger factor, in case of thousands of records */
    heap->rec_alloced = heap->rec_count + 1;
  }
  /* add the new record onto the very end of the heap */
  heap->records[heap->rec_count] = *rec;
  heap->rec_count += 1;
  /* while the new record is less than its parent */
  /* exchange the new record with it's parent */
}

word_rec pop_record(word_heap * heap) {
  word_rec ret;
  if (heap->rec_count == 0) {
    fprintf(stderr,"ERROR: popped empty word_heap");
    exit(1);
  }
  ret = heap->records[0];
  /* replace the root node of the heap with the last node*/
  heap->records[0] = heap->records[heap->rec_count - 1];
  heap->rec_count -= 1; /*don't clear the old last node, we'll use it as swap space */
  /* while the (former last) new root node is less than either of its children*/
  
  /* switch its position with that child.  Keep iterating on the former last node, not the root) */

  /* return the prior root node; we may update it and re-insert */  
  memset(heap->records + heap->rec_count + 1, 0, sizeof(word_rec));
  return ret;
}

void dump_hits(dbh *db, uint32_t *hits, int count) {
  int i,j;
  for(i = 0; i < count; i++) {
    for (j = 0; j < db->dbspec->fields; j++) {
      if (j != 0) { fprintf(stdout," "); }
      fprintf(stdout,"%d", hits[j+i*db->dbspec->fields]);
    }
    fprintf(stdout,"\n");
  }
}

int main(int argc, char **argv) {

  char buffer[256];
  dbh *db;
  char word[256];
  int32_t *hits;
  word_rec rec;
  word_heap heap;
  int i,j;

  db = init_dbh_folder(argv[1]);
  heap = new_heap(db);
  while(fgets(buffer,256,stdin)) {
    sscanf(buffer,"%s256",word);
    fprintf(stderr, "looking up %s : ",word);

    //word_lookup(db,word);
    rec = fetch_word(db,word);
    //rec = new_word_rec(db,word);

    if (rec.type == 0) {
      fprintf(stderr, "%s: %d hits in header\n", rec.word, (int)rec.freq);
      dump_hits(db, rec.header_hits, rec.freq);
    } else {
      fprintf(stderr, "%s: %d hits in %d blocks @ %d\n", rec.word, (int)rec.freq, rec.block_count, (int)rec.start_offset);
      dump_hits(db, rec.header_hits, rec.block_count);
    }
    add_record(&heap,&rec);
  }
  fprintf(stdout, "word_heap has %d records\n", i);
  for (j = 0; j < heap.rec_count; j++) {
    fprintf(stderr,"%s\n",heap.records[j].word); 
  }
  start_stream(&heap);
  return 0;
}
