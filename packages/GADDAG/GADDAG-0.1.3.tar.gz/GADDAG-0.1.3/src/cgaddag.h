#ifndef GADDAG_H_INCLUDED
#define GADDAG_H_INCLUDED

void add_word(GADDAG, char*);
int has(GADDAG, char*);
List starts_with(GADDAG, char*);
List contains(GADDAG, char*);
List ends_with(GADDAG, char*);
GADDAG newGADDAG();
#endif
