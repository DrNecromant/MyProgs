#include<stdio.h>
#include<stdarg.h>
#include<time.h>

#include"mytypes.h"

#define ERROR 0x0001
#define INFO 0x0002
#define WARNING 0x0003
#define DEBUG 0x0004

//errors
#define ALLOC_ERR 0x8000

#define _error(ap, fmt) {va_start(ap, fmt);trace(fmt, ap, ERROR);va_end(ap);}
#define _info(ap, fmt) {va_start(ap, fmt);trace(fmt, ap, INFO);va_end(ap);}
#define _warning(ap, fmt) {va_start(ap, fmt);trace(fmt, ap, WARNING);va_end(ap);}
#define _debug(ap, fmt) {va_start(ap, fmt);trace(fmt, ap, DEBUG);va_end(ap);}

#define _max_alloc_size 1000000
#define _max_word_lenght 100

int dbglvl = INFO;

static char _alloc_buf[_max_alloc_size];
static char _word[_max_word_lenght];
static charp _alloc_p = _alloc_buf;

static va_list ap;

static FILE *_file_read = NULL, *_file_write = NULL;

static void trace(const charp fmt, va_list ap, int trace_lvl)
{
	switch(trace_lvl) {
		case ERROR: {
			printf("ERROR:\t\t");
			break;
		}
		case INFO: {
			printf("INFO:\t\t");
			break;
		}
		case WARNING: {
			printf("WARNING:\t");
			break;
		}
		case DEBUG: {
			printf("DEBUG:\t\t");
			break;
		}
	}
	vprintf(fmt, ap);
	printf("\n");
}

void error(const charp fmt, ...)
{
	if(dbglvl >= ERROR)
		_error(ap, fmt);
}

void info(const charp fmt, ...)
{
	if(dbglvl >= INFO)
		_info(ap, fmt);
}

void warning(const charp fmt, ...)
{
	if(dbglvl >= WARNING)
		_warning(ap, fmt);
}

void debug(const charp fmt, ...)
{
	if(dbglvl >= DEBUG)
		_debug(ap, fmt);
}

char getEOF() {
	return(EOF);
}

char getChar()
{
	return(getc(_file_read));
}

void putChar(char c)
{
	putc(c, _file_write);
}

static int ctoi(char c) {
	return(c - '0');
}

void setDebugLevel(charp arg)
{
	dbglvl = ctoi(*arg);
}

static charp alloc(int n)
{
	if(_alloc_p + n <= _alloc_buf + _max_alloc_size) {
		_alloc_p += n;
		return(_alloc_p - n);
	}
	else {
		return(NULL);
	}
}

static intchainp challoc()
{
	return((intchainp) alloc(sizeof(struct intchain)));
}

static treep talloc()
{
	return((treep) alloc(sizeof(struct tree)));
}

void openFileRead(charp filename)
{
	_file_read = fopen(filename, "r");
}

void openFileWrite(charp filename)
{
	_file_write = fopen(filename, "w");
}

void closeFiles()
{
	fclose(_file_read);
	fclose(_file_write);
}

static int saveChainEl(intchainp *ch, int value)
{
	debug("=== save chain element ===");
	intchainp link;
	if(!*ch) {
		debug("CHAIN: init chain");
		*ch = challoc();
		if(!*ch) {
			return ALLOC_ERR;
		}
		link = *ch;
	}
	else {
		link = *ch;
		while(link->next) {
			link = link->next;
		}
		debug("CHAIN: create link");
		link->next = challoc();
		if(!link->next) {
			return ALLOC_ERR;
		}
		link = link->next;
	}
	debug("CHAIN: set value %d", value);
	link->value = value;
	return 0;
}

int saveTreeEl(treep *t, char c, int pos)
{
	int ret;
	debug("=== save tree element %c on pos %d ===", c, pos);
	treep branch;
	if(!*t) {
		debug("TREE: init tree");
		*t = talloc();
		if(!*t) {
			return ALLOC_ERR;
		}
		branch = *t;
		debug("TREE: set value, %c", c);
		branch->value = c;
		branch->count = 0;
	}
	else {
		branch = *t;
		while(c != branch->value) {
			if(c > branch->value) {
				if(!branch->right) {
					debug("TREE: create right");
					branch->right = talloc();
					if(!branch->right) {
						return ALLOC_ERR;
					}
					debug("TREE: set value %c", c);
					branch->right->value = c;
					branch->right->count = 0;
				}
				branch = branch->right;
			}
			else if(c < branch->value) {
				if(!branch->left) {
					debug("TREE: create right");
					branch->left = talloc();
					if(!branch->left) {
						return ALLOC_ERR;
					}
					debug("TREE: set value %c", c);
					branch->left->value = c;
					branch->left->count = 0;
				}
				branch = branch->left;
			}
		}
	}
	debug("TREE: set count %d", (branch->count + 1));
	branch->count++;
	ret = saveChainEl(&branch->pos, pos);
	return ret;
}

int getTime()
{
	return time(NULL);
}
