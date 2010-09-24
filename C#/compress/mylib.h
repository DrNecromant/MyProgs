#include "mytypes.h"

//functions to write trace in output
void error(const charp fmt, ...);
void info(const charp fmt, ...);
void warning(const charp fmt, ...);
void debug(const charp fmt, ...);

//get EOF value
char getEOF();

//just get char
char getChar();

//just get char
void putChar(char c);

//set debug lvl from arg
void setDebugLevel(charp arg);

//open file for reading
void openFileRead(charp filename);

//open file for writing
void openFileWrite(charp filename);

//close read-write files
void closeFiles();

//save element in struct tree
int saveTreeEl(treep *t, char c, int pos);

//get first char from integer
char getCharFromInt1(int a);

//get second char from integer
char getCharFromInt2(int a);

//get integer from two chars
int getIntFromChars(char c1, char c2);

//get current time in seconds
int getTime();
