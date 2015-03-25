#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
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
  uint64_t total_freq;
  size_t rec_count;
  size_t rec_alloced;
  int (*cmp)(dbh *,word_rec , word_rec );
  uint32_t *current_hit;
  char *current_word;
} word_heap;

typedef struct corpus {
  char * fn;
  FILE * fh;
  uint32_t *current_hit;
} corpus;

enum stage_kind {
  CORPUS,
  HEAP
};

typedef struct search_stage {
  enum stage_kind kind;
  int (*check)(dbh *,uint32_t *,uint32_t *, int);
  int arg;
  int init;
  union {
    word_heap heap;
    corpus corp;
  } data;
} search_stage;

word_rec * fetch_word(dbh *db, char *word) {
  word_rec rec;
  word_rec *ret;
  datum key,val;
  int len,pos,block_size,header_hits;
  char *buffer;

  ret = malloc(sizeof(word_rec));  
  rec.word = malloc(strlen(word) + 1);
  strcpy(rec.word,word);

  key.dptr = word;
  key.dsize = strlen(word);

  val = gdbm_fetch(db->hash_file,key);
  if (val.dptr == NULL) {
    return NULL;
    //    return 0; ?? probably need to make this a pointer type and return null.
  }
  len = val.dsize << 3; // size of the vector in bits

  rec.header = bitsvectorNew((char *)val.dptr);

  buffer = malloc(sizeof(char) * db->dbspec->block_size);
  rec.block = bitsvectorNew(buffer);

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
  //fprintf(stderr,"%s at bit %d of %d; %d hits remaining in header.\n",rec.word,pos,len,header_hits);
  if (rec.type == 1) {
    rec.block_count = header_hits; 
  } else { 
    rec.block_count = 0;
  }
  
  rec.current_block = 0; // is this redundant with header_position?
  rec.header_position = 0; 
  rec.block_position = 0; // position 0 means the header is the next hit, and the block hasn't been -ed yet.
  rec.current_hit = calloc(1,db->dbspec->fields * sizeof(uint32_t));
  rec.next_header = calloc(1,db->dbspec->fields * sizeof(uint32_t));
  *ret = rec;
  return ret;
}

void read_hit(dbh *db, bitsvector *v, uint32_t *hits) {
  int i;
  for (i = 0; i < db->dbspec->fields; i++) {
    hits[i] = bitsvectorGet(v,db->dbspec->bitlengths[i]);
  }
}

uint32_t *word_next_hit(dbh *db, word_rec *rec) {
  bitsvector peek;
  int res,i;
//  char *buffer;
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
    //fprintf(stderr,"type %d; in block %d of %d", rec->type, rec->current_block, rec->block_count);
    if (rec->current_block < rec->block_count) { // if we aren't past the last block
      if (rec->block_position == 0) { // if we need to start a new block...
//      fprintf(stderr,", reading header for block %d of %d\n",rec->current_block, rec->block_count);

        // read the header.
        read_hit(db,rec->header,rec->current_hit); 
        rec->header_position += 1;
        rec->block_position += 1; // note that we haven't actually read from a block, or loaded it
    
        // free the old block vector
//        if (rec->block != NULL) {
//          fprintf(stderr,"freeing rec->block on %s\n", rec->word);
//          bitsvectorOld(rec->block);
//          rec->block = NULL;
//        }
    
        // peek at the next header hit, if we're not on the last block
        if (rec->header_position < rec->block_count) {
          //fprintf(stderr,", looking ahead at next block");
          peek = *rec->header; // save the state of the header vector
          read_hit(db,rec->header,rec->next_header); // read the next block's header
          *rec->header = peek; // rewind
        } else { // if we're on the last block
          rec->next_header = NULL;
        }
        //fprintf(stderr,"\n");
        return rec->current_hit;
      }
      else { // if we've read the header of the current block..
        // we may still need to load it from disk.
        if (rec->block_position == 1) {
//          fprintf(stderr,"%s: loading block from disk\n", rec->word);
//          buffer = malloc(sizeof(char) * db->dbspec->block_size);
          res = fseeko(db->block_file,rec->start_offset + (db->dbspec->block_size * (rec->current_block))  ,0);
          res = fread(rec->block->v,sizeof(char),db->dbspec->block_size, db->block_file);
          // ugly.  should port back to bitsVector.
          rec->block->o = 0;
          rec->block->s = 0;
          rec->block->b = 0;
          
//          rec->block = bitsvectorNew(buffer); // buffer will be freed when bitsvectorOld is called.
        } 
//        fprintf(stderr, "%s: at bit %d in block\n", rec->word, bitsvectorTell(rec->block) );

        // we should check to see if we're still in a block--don't know why this doesn't segfault.
        if ( bitsvectorTell(rec->block) + db->dbspec->bitwidth > db->dbspec->block_size << 3) {
          //fprintf(stderr,"end of block, advancing to next block\n");
          rec->current_block += 1;
          rec->block_position = 0;
          return word_next_hit(db,rec);
        }
//        fprintf(stderr,"%s: reading block %d hit %d at bit %d of %d\n",rec->word,rec->current_block,rec->block_position,bitsvectorTell(rec->block),db->dbspec->block_size << 3);
        // once it's loaded, read it into a temp buffer.
        read_hit(db,rec->block,rec->current_hit);
        // a hit consisting of all binary 1's is actually an end-of-block flag
        for (i = 0; i < db->dbspec->fields; i++) {
          if (rec->current_hit[i] != (( 1 << db->dbspec->bitlengths[i] ) - 1 )) {
            //fprintf(stderr,":valid");
            // the hit is good, return it.
            rec->block_position += 1;
	    // fprintf(stderr, "%s: at bit %d after reading hit\n", rec->word, bitsvectorTell(rec->block));
            //fprintf(stderr,"; advancing to block hit %d\n",rec->block_position);
            return rec->current_hit;
          }
        }
        //fprintf(stderr,":invalid, advancing to next block\n");
        // the hit is fake, we need to go to the next block.
        rec->current_block += 1;
        rec->block_position = 0;
        // call ourselves recursively, we can check there if we've gone off the last block.
        return word_next_hit(db,rec);
      }
    }
    else { // if we're off the end of the block list
      // fprintf(stderr,"%s: no more blocks.  returning NULL\n", rec->word);
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
  rec.word = malloc(strlen(word) + 1);
  strcpy(rec.word,word);
  
  rec.current_block = 0;
  
  return rec;
}

void dump_hits(FILE *f,dbh *db, uint32_t *hits, int count) {
  int i,j;
  for(i = 0; i < count; i++) {
    for (j = 0; j < db->dbspec->fields; j++) {
      if (j != 0) { fprintf(f," "); }
      fprintf(f,"%d", hits[j+(i*db->dbspec->fields)]);
    }
    fprintf(f,"\n");
  }
}

void dump_hit(FILE *f, uint32_t *hits, int count, int newline) {
	int i;
	for (i = 0; i < count; i++) {
		if (i != 0) fprintf(f," ");
		fprintf(f,"%d", hits[i]);
	}
	if (newline != 0) fprintf(f,"\n");
}

int byte_cmp(dbh *db, uint32_t *L, uint32_t *R, int arg) {
  //fprintf(stderr, "byte_cmp'ing %d %d : %d %d\n", L[0], L[7], R[0], R[7]);
  if (L[0] != R[0]) {
    return L[0] < R[0] ? -1 : 1;
  } else if (L[7] != R[7]) {
    return L[7] < R[7] ? -1 : 1;
  } else {
    return 0;
  }
}

int hit_cmp(dbh *db, uint32_t *L, uint32_t *R, int arg) {
  int i;
  for (i = 0; i < 7; i++) { //ugly...db has 9 fields, only 7 are good for sorting
    if (L[i] != R[i] ) {
      return L[i] < R[i] ? -1 : 1;
    }
  }
  return 0;
}

int contains_cmp(dbh *db, uint32_t *L, uint32_t *R, int arg) {
  int i;
  for (i = 0; i < 7; i++) {
    if (L[i] == 0) { return 0; }
    if (L[i] != R[i] ) {
      return L[i] < R[i] ? -1 : 1;
    }
  }
  return 0;
}

int proximity_cmp(dbh *db, uint32_t *L, uint32_t *R, int arg) {
  int i;
  int dist;
  for (i = 0; i < 6; i++) { //ugly...db has 9 fields, only 7 are good for sorting
    if (L[i] != R[i] ) {
      return L[i] < R[i] ? -1 : 1;
    }
  }
  dist = R[6] - L[6];
  if ((arg >= dist) && (dist > 0)) {
    return 0; // this could be tricky when SKIPPING is implemented
  }
  else if (dist < arg) {
    return 1;
  } else {
    return -1;
  }
}

int phrase_cmp(dbh *db, uint32_t *L, uint32_t *R, int arg) {
  int i;
  int dist;
  for (i = 0; i < 6; i++) { //ugly...db has 9 fields, only 7 are good for sorting
    if (L[i] != R[i] ) {
      return L[i] < R[i] ? -1 : 1;
    }
  }
  dist = R[6] - L[6];
  if (arg == dist) {
    return 0; // this could be tricky when SKIPPING is implemented 
  }
  else if (dist < arg) {
    return 1;
  } else {
    return -1;
  }
  //    return dist < (uint32_t) arg ? 1 : -1; // is this right?
}

int sent_cmp(dbh *db, uint32_t *L, uint32_t *R, int arg) {
  int i;
  uint32_t dist;
  
  for (i = 0; i < 6; i++) { //ugly...db has 9 fields, only 7 are good for sorting
    if (L[i] != R[i] ) {
      fprintf(stderr,"mismatch at %d\n",i);
      return L[i] < R[i] ? -1 : 1;
    }
  }
  return 0;
}

int rec_cmp(dbh *db, word_rec L, word_rec R) {
  //fprintf(stderr, "comparing %s <> %s\n", L.word, R.word);
  //return hit_cmp(db,L.current_hit,R.current_hit);
  return byte_cmp(db,L.current_hit,R.current_hit,0);
}

word_heap new_heap(dbh * db) {
  word_heap heap;
  heap.db = db;
  heap.records = NULL;
  heap.total_freq = 0;
  heap.rec_count = 0;
  heap.rec_alloced = 0;
  heap.cmp = rec_cmp;
  heap.current_hit = calloc(1,db->dbspec->fields * sizeof(uint32_t));
  heap.current_word = NULL;
  return heap;
}

int lchild(int i) {
  return (2*i) + 1;
}

int rchild(int i) {
  return (2*i) + 2;
}

int parent(int i) {
  return floor((double)(i - 1)/2.0);
}

void dump_heap(word_heap *heap) {
  int i;
  for (i = 0; i < heap->rec_count; i++) {
  	fprintf(stderr,"%s\t", heap->records[i].word);
  	dump_hit(stderr, heap->records[i].current_hit,9,1);  
  }
}

int up_heap(word_heap *heap, int i) {
  word_rec rec;
  int cmp_res;
  int p = parent(i);
  dbh *db = heap->db;
  word_rec *records = heap->records;
  // bounds check
  if (i == 0) { return 0; }
//  cmp_res = heap->cmp(db, heap->records[i], records[parent(i)]);
//  fprintf(stderr,"testing for up_heap: [%d]:%s ",i, records[i].word);
//  dump_hit(stderr, records[i].current_hit,9,0);
//  fprintf(stderr," vs [%d]:%s", p,records[p].word);
//  dump_hit(stderr, records[p].current_hit,9,0);
//  fprintf(stderr," returns %d\n",cmp_res);
  if ( heap->cmp(db, heap->records[i], records[parent(i)]) < 0) {
//    fprintf(stderr,"up-swapping %s @ %d with %s @ %d\n", records[i].word,i, records[p].word,p);
    rec = records[i];
    records[i] = records[parent(i)];
    records[parent(i)] = rec;
    up_heap(heap,parent(i));
    return 1; 
  }
  return 0;
}

int down_heap(word_heap *heap, int i) {
  word_rec rec;
  int child = 0;
  dbh *db = heap->db;
  word_rec *records = heap->records;
  int lres, rres;
//  fprintf(stderr, "pre down_heap(%d):\n",i);
//  fprintf(stderr,"down_heap %d with L %d, R %d ):",i,lchild(i), rchild(i) );
  // bounds check
  if (lchild(i) >= heap->rec_count) { 
//    fprintf(stderr, "%d is leaf in heap size %d\n",i,heap->rec_count);
    return 0;
  } // if we have a leaf, return 0;
  // if this is a partially filled branch, only check left
  else if (rchild(i) >= heap->rec_count) { 
//    fprintf(stderr, "%d is partial branch with leaf in heap size %d\n",i,lchild(i),heap->rec_count);
    if ( heap->cmp(db, records[i], records[lchild(i)]) > 0) {
      child = lchild(i);
    }
  }
  // normal case: if i is greater than either of its children
  else {
//    fprintf(stderr,"%d is normal branch with leaves %d,%d,in heap size %d\n",i,lchild(i),rchild(i),heap->rec_count);
    if ( (heap->cmp(db, records[i], records[lchild(i)]) > 0) ||
       (heap->cmp(db, records[i], records[rchild(i)]) > 0) ) {  
      if (heap->cmp(db, records[lchild(i)], records[rchild(i)]) < 0) {
      // swap i with it's lesser child
    //fprintf(stderr,"swapping left; ");
    child = lchild(i);
      } else {
    //fprintf(stderr,"swapping right; ");
    child = rchild(i);
      }
    }
  }
  if (child > 0) { // if we found a child to swap with
//    fprintf(stderr,"down-swapping %s @%d with %s @ %d\n", records[i].word,i, records[child].word,child);
    rec = records[i];
    records[i] = records[child];
    records[child] = rec;    
//    dump_heap(heap);
    down_heap(heap,child);
    return 1;
  }
  return 0;
}

void add_record(word_heap *heap, word_rec *rec) {
  /* first make space if needed */
  int i;
  fprintf(stderr,"heap has %d records\n", heap->rec_count);
  if (heap->rec_count <= heap->rec_alloced) {
    /* should check for success here; running out of memory is a concern */
    heap->records = realloc(heap->records,sizeof(word_rec)*(heap->rec_count+1) );
    /* should also consider expanding by a larger factor, in case of thousands of records */
    heap->rec_alloced = heap->rec_count + 1;
  }
  /* fetch the first hit so the record is ready for use */
  word_next_hit(heap->db,rec);
  /* add the new record onto the very end of the heap */
  heap->records[heap->rec_count] = *rec;
  heap->rec_count += 1;
  heap->total_freq += rec->freq;
  /* while the new record is less than its parent */
  /* exchange the new record with it's parent */ 
  //fprintf(stderr, "calling up_heap on new record %d\n", heap->rec_count - 1);
  up_heap(heap,heap->rec_count - 1);
  fprintf(stderr,"heap order:\n");
  //dump_heap(heap);
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
  down_heap(heap,0);
  /* return the prior root node; we may update it and re-insert */  
  // no we won't; clean up memory here?  
  // SUSPICIOUS
  //  memset(heap->records + heap->rec_count + 1, 0, sizeof(word_rec));
  return ret;
}

word_rec * add_word(word_heap *heap, char *word) {
  word_rec *rec = NULL;
  rec = fetch_word(heap->db,word);
  if (rec == NULL) {
    fprintf(stderr, "%s not found.\n", word);
    return NULL;
  }
  else {
    fprintf(stderr, "%s has %lld occurrences.\n", word, rec->freq);
    add_record(heap,rec);
    free(rec);
  }
}

uint32_t * heap_advance(word_heap *heap) {
  word_rec *r;
  uint32_t *hit;
  if (heap->rec_count == 0) {
    // fprintf(stderr, "stage done\n");
    heap->current_hit = NULL;
    return NULL;
  } else {
    r = &heap->records[0];
    // this is suspicious.
    memcpy(heap->current_hit, r->current_hit, heap->db->dbspec->fields * sizeof(uint32_t) );
    heap->current_word = r->word;
    
    if (heap->current_word[0] == 0) {
//      fprintf(stderr, "%s: zero in heap hit\n", heap->current_word);
    }
    hit = word_next_hit(heap->db,r);
    if (hit == NULL) {
//      fprintf(stderr, "done with word %s, popping\n", heap->current_word);
      // if we are done with the word, pop it off
      pop_record(heap);
//      fprintf(stderr, "heap has %d records remaining\n", heap->rec_count);
    } else {
      // otherwise, we've modified the 0 records and may need to move it.
      down_heap(heap,0); 
      if (hit[0] == 0) {
//		fprintf(stderr, "zero at top of heap\n");
      }
    }
    return heap->current_hit;
  }
}

uint32_t * corpus_advance(corpus *corpus) {
  // requires that corpus has a readable fh and malloc'd current_hit.  Does not require current_hit to be init'd.
//  fprintf(stderr, "advancing corpus: ");
  size_t res = fread(corpus->current_hit,sizeof(uint32_t), 7, corpus->fh); // read 1 7-wide hit into current_hit
  if (res < 7) {
    fprintf(stderr, "READ FAILED %d\n",res);
    corpus->current_hit = NULL;
    return NULL;
  } else {
//    fprintf(stderr, "%d %d %d %d %d %d %d\n", corpus->current_hit[0],corpus->current_hit[1],corpus->current_hit[2],corpus->current_hit[3],corpus->current_hit[4],corpus->current_hit[5],corpus->current_hit[6]);
    return corpus->current_hit;
  }  
}

uint32_t * stage_advance(search_stage * stage) {
  if (stage->kind == CORPUS) {
    return corpus_advance (&stage->data.corp);
  } else if (stage->kind == HEAP) {
    return heap_advance (&stage->data.heap);
  }
}

uint32_t * stage_current_hit(search_stage * stage) {
  if (stage->kind == CORPUS) {
    return stage->data.corp.current_hit;
  } else if (stage->kind == HEAP) {
    return stage->data.heap.current_hit;
  }
}

uint32_t * init_stage_heap(search_stage * stage, word_heap * heap, void * search_method,int search_method_arg) {
  stage->kind = HEAP;
  stage->data.heap = *heap; //worrisome
  stage->check = search_method; // wrong method
  stage->arg = search_method_arg;
  stage->init = 0;
//  return stage_advance(stage);
  return NULL;
}

uint32_t * init_stage_corp(search_stage * stage, corpus *corpus) {
  stage->kind = CORPUS;
  stage->data.corp = *corpus; //worrisome
  stage->check = contains_cmp;  
  stage->init = 0;
  //  return stage_advance(stage);
  return NULL;
}

int dump_search_result_ascii(FILE * fh,search_stage * stages, int size) {
  int i;
  int j;
  uint32_t * hit;
  int first_word = 1;
  for (i = 0; i < size; i++) {      
    hit = stage_current_hit(&stages[i]);
    if (stages[i].kind == HEAP) {
      if (first_word == 1) {
        first_word = 0;
        fprintf(fh, "%d %d %d %d %d %d %d %d %d", hit[0],hit[1],hit[2],hit[3],hit[4],hit[5],hit[6],hit[7],hit[8]);
      }
      else {
        fprintf(fh, " :: %d %d %d %d %d %d %d %d %d", hit[0],hit[1],hit[2],hit[3],hit[4],hit[5],hit[6],hit[7],hit[8]);
      }            
    } else {
      fprintf(fh, "(%d %d %d %d %d %d %d) ", hit[0],hit[1],hit[2],hit[3],hit[4],hit[5],hit[6]);
    }
  }
  fprintf(fh, "\n");
  return 0;
}

int dump_search_result_binary(FILE * fh,search_stage *stages, int size) {
  int i;
  uint32_t * hit;
  int first = 1;
  for (i = 0; i < size; i++) {
    hit = stage_current_hit(&stages[i]);
    if (stages[i].kind == HEAP) {
      if (first == 1) {
        // hit prefix up to sentence--same for all hits.
        fwrite(hit,sizeof(uint32_t),6,fh);
        // hit page number of first word
        fwrite(&hit[8],sizeof(uint32_t),1,fh);
        first = 0;
      }
      // word and byte for each word
      fwrite(&hit[6],sizeof(uint32_t),2,fh);
    }  
  }
  return 0;
}

uint32_t * search_advance(search_stage *stages,int size) {  
  int c = size - 1;        // our position in the stages array; start at the end
  int check_res;           // the result of the previous stage's search predicate function
  uint32_t * advance_res;  // the result of advancing the current or previous stage--not actually used directly.
  int i;
  int starting_stage = c;
  search_stage * curr = &stages[c]; // we should probably assign curr to the least stage, not the last
  search_stage * prev;     // not assigned until we know it is safe.
  // fprintf(stderr, "advancing stage %d : ", c);

  // We have decided to switch to a unique-pairs matching algorithm, which means all words,
  // but not corpus stages, should be advanced at the start of each search_advance call;

  while (c >= 0) {
    curr = &stages[c];
    if (curr->kind == HEAP) {
      advance_res = stage_advance(curr); // advance the last stage. must do this at least once. 
      curr->init = 1;
      if (c > 0) {
	starting_stage = c;
      }
      c -= 1;
    } else {
      break;
    }
  }

  c = starting_stage;

  // could set init on curr here, or elsewhere. 
  if (size == 1) {                    // if this is a one-stage search, we're done.
    return stage_current_hit(curr);   // if current hit is NULL this returns NULL, so don't need to check explicitly.
  }
  
  // otherwise, search checks proceed from right to left, or outer to inner, or size - 1 to 1.
  // when we advance a stage, we have to check it against it's preceding/inner stage

  while (1) {
    curr = &stages[c];
    prev = &stages[c - 1]; // we know that this is safe, because we always check that c > 1 before decrementing.

    if (prev->init == 0) {
        advance_res = stage_advance(prev);
        prev->init = 1;
        if (c > 1) {
          c -= 1;
	  // should probably continue here to force init of longer queries?
	  continue;
        }
    }

    // fprintf("stage %d at block %d bit %d; \n", c, curr->data.heap.records[0].block_count,bitsvectorTell(curr->data.heap.records[0].block));

    // curr is always the stage that was just advanced.  So we can check to see if it has run out of hits.
    if (stage_current_hit(curr) == NULL) {
      return NULL;
    } else if (stage_current_hit(prev) == NULL) {
      return NULL;
    }
    
    if ( (stage_current_hit(curr)[0] == 0) || (stage_current_hit(prev)[0] == 0) ) {
      //fprintf(stderr, "WHOA!\n");
    }
    //fprintf(stderr,"pre checking: ");
    //dump_search_result_ascii(stderr,stages, size);

    check_res = prev->check(NULL, stage_current_hit(prev),stage_current_hit(curr),prev->arg);

//    fprintf(stderr,"post checking(result: %d) ",check_res);
    //dump_search_result_ascii(stderr,stages, size);

    if (check_res < 0) {         // if curr is ahead of prev, advance prev
//      fprintf(stderr, "advancing L\n");
      if (stage_current_hit(prev) != NULL) {
	//  fprintf(stderr,"pre L-advance: ");
        //dump_search_result_ascii(stderr,stages, size);
      }
      advance_res = stage_advance(prev);
      if (c > 1) {               // since we've advanced prev, if it is not the innermost hit, we have to check it against it's own prev stage in the next loop cycle
        c -= 1;
      } 
      if (stage_current_hit(prev) != NULL) {
	//fprintf(stderr,"post L-advance: ");
	//dump_search_result_ascii(stderr,stages, size);
      }

    } else if (check_res == 0) { // if curr and prev are within the window defined by prev's search check function...
      if (c == size - 1) {       // if we're on the outermost hit, it's good to output    
//        fprintf(stderr,"match\n");
        return stage_current_hit(curr);
      } else {                   // if we are on an inner hit, we can move our c counter outward.        
//        fprintf(stderr,"partial match\n");
        c += 1;
      }

    } else if (check_res > 0) {  // if prev is ahead of curr, advance curr
//      fprintf(stderr, "advancing R\n");
      advance_res = stage_advance(curr);
    }
  }
}

// NOTES for above:
  // while true:
  //   if current = 0: break
  //   prev = current - 1
  //   res = check (prev,current)  // attach the check function to current or prev?
  //   if res < 0:
  //     advance prev
  //     current = prev  // having advanced the prev stage, we should check and focus on it.
  //   else if res > 0:
  //     advance current // we can just keep pushing the current stage forward and checking.
  //   else if res == 0: // otherwise this stage is a match, but we have to check that we haven't passed any succeeding stages.
  //     if current == last:
  //       return current
  //     else:
  //       current = current + 1


int main(int argc, char **argv) {

  char buffer[256];
  dbh *db;
  char * corpus_fn;
  char * search_method_name;
  char * search_method_arg_str;
  int (*search_method)(dbh *,uint32_t *,uint32_t *, int);
  int search_method_arg;
  char * output_arg;
  int (*dump_search_result)(FILE *, search_stage *,int);
  char word[256];
  int32_t *hits;
  word_rec *rec;
  word_heap heap;
  int i,j;
  int optc;
  int read;
  search_stage stages[20];
  int stage_c = 0;
  corpus corp;
  uint32_t * search_res;
  
  search_method = &phrase_cmp;
  search_method_arg = 1;
  dump_search_result = &dump_search_result_ascii;

  while ((optc = getopt(argc, argv, "c:m:a:o:")) != -1) {
    switch (optc) {
    case 'c': // corpus file
      fprintf(stderr, "corpus '%s'\n", optarg);
      corpus_fn = optarg;
      corp.fn = corpus_fn;
      corp.fh = fopen(corp.fn,"r");
      corp.current_hit = malloc(7 * sizeof(uint32_t));
      // probably init corpus by hand here, since it can't come from anywhere else.
      init_stage_corp(&stages[0],&corp);
      stage_c = 1;
      break;
    case 'm': // search method
      fprintf(stderr, "method '%s'\n", optarg);
      search_method_name = optarg;      
      if (strcmp(search_method_name, "phrase") == 0) search_method = phrase_cmp;
      else if (strcmp(search_method_name, "proxy") == 0) search_method = proximity_cmp;
      else if (strcmp(search_method_name, "sent") == 0) search_method = sent_cmp;
      else if (strcmp(search_method_name, "cooc") == 0) search_method = sent_cmp;
    case 'a': // search method argument
      fprintf(stderr, "arg is '%s'\n", optarg);
      search_method_arg_str = optarg;
      sscanf(optarg,"%d",  &search_method_arg);
      break;
    case 'o': // output mode
      fprintf(stderr, "output '%s'\n", optarg);
      output_arg = optarg;
      if (strcmp(output_arg, "binary") == 0) dump_search_result = &dump_search_result_binary;
    case ':': // missing option argument
      break;
    case '?': // unrecognized
      break;
    default:
      break;
    }
  }

  // optind should now point at the non-option arg, which is the db folder path
  db = init_dbh_folder(argv[optind]);
  heap = new_heap(db);
  while(fgets(buffer,256,stdin)) {

    if (strcmp("\n",buffer) == 0) {
      init_stage_heap(&stages[stage_c],&heap,search_method,search_method_arg);
      stage_c += 1;
      if (stage_c == 20) { // if we've exceeded the max stage limit, unlikely.
        exit(1);
      }
      heap = new_heap(db);
    } else {
      sscanf(buffer,"%s256",word);
      fprintf(stderr, "looking up %s : \n",word);
      rec = add_word(&heap,word);    
    }
  }

// clean up last stage

  fprintf(stderr, "done scanning input\n");
  init_stage_heap(&stages[stage_c],&heap,search_method,search_method_arg);
  fprintf(stderr, "output for %d stages\n", stage_c + 1);
  while (stage_current_hit(&stages[stage_c]) != NULL) {
    // if this is not the intial stage, print the current hit;
    if (stages[stage_c].init == 1) {
      // fprintf(stdout, "MATCH");
      dump_search_result(stdout,stages,stage_c + 1);
    }
    search_res = search_advance(stages,stage_c + 1);
    if (search_res == NULL) {
      fprintf(stderr,"search_advance returned NULL, done\n");
      break;
    }
  }

  return 0;
}
