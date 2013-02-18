// $Id: dbspecs.H,v 2.10 2004/05/28 19:22:02 o Exp $
/*
 * Database-specific constants
 */

#define  FIELDS 9

#define  BLK_SIZE       2048
#define  TYPE_LENGTH    1
#define  FREQ1_LENGTH   4

#define  NEGATIVES      {0,1,1,1,1,1,0,0,0}
#define  DEPENDENCIES   {-1,0,1,2,3,4,5,0,7}


#define BITLENGTHS      {13,12,11,9,13,12,14,24,14}
#define  FREQ2_LENGTH    25
#define  OFFST_LENGTH    33

