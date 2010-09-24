#include "mylib.h"

//error consts
#define PARSING_ERR 0x2000

//error string
#define ALLOC_ERR_STR "Allocation error"
#define PARSING_ERR_STR "Invalid usage"

int parseArgs(int argc, char **argv);

int main(int argc, char **argv)
{
	treep storage = 0;
	char c;
	int i = 0;
	int ret;

	ret = parseArgs(argc, argv);
	if(ret) {
		error(PARSING_ERR_STR);
		return ret;
	}

	info("Start compressing");
	while((c = getChar()) != getEOF()) {
		ret = saveTreeEl(&storage, c, i++);
		if(ret) {
			error(ALLOC_ERR_STR);
			return ret;
		}
	}
	info("letters count %d", i);
	saveTree(storage);
	closeFiles();
	return 0;
}

int parseArgs(int argc, char **argv)
{
	charp fileread = 0, filewrite = 0;
	int argn = argc;
	charp arg;

	while(argn-- > 1) {
		arg = argv[argc - argn];
		if(*arg == '-') {
			switch(*++arg) {
				case 'd': {
					setDebugLevel(++arg);
					break;
				}
			}
		}
		else if(!fileread) {
			fileread = arg;
		}
		else if(!filewrite) {
			filewrite = arg;
		}
	}
	if(!filewrite || !fileread) {
		return PARSING_ERR;
	}
	debug("Get files to compress: %s, %s", fileread, filewrite);
	openFileRead(fileread);
	openFileWrite(filewrite);
	return 0;
}

saveTree(treep t) {
	intchainp p;
	int diff, pvalue = 0;
	if(t != 0) {
		saveTree(t->left);
		debug("%c, %d", t->value, t->count);
		putChar(t->value);
		putChar(getCharFromInt2(t->count));
		putChar(getCharFromInt1(t->count));
		p = t->pos;
		while(p) {
			diff = p->value - pvalue;
			putChar(getCharFromInt2(diff));
			putChar(getCharFromInt1(diff));
			debug("%d, %d", p->value, diff);
			pvalue = p->value;
			p = p->next;
		}
		saveTree(t->right);
	}
	return 0;
}
