//Program for compress-decompress files
//
//Compressor save chars into tree struct:
//      value
//	count
//	char position struct:
//		value
//		->next
//	->right (the bigger char)
//	->left (the smaller char)
//After that write tree into read file:
//char(byte).count(2bytes).positions(2bytes each)...
//
//Decompressor read file and write chars
//into write file according char position
//with fseek()

#include "mylib.h"

//error consts
#define PARSING_ERR 0x2000

//error string
#define ALLOC_ERR_STR "Allocation error"
#define PARSING_ERR_STR "Invalid usage"

//decompress flag
int dec = 0;

int parseArgs(int argc, char **argv);

int main(int argc, char **argv)
{
	treep storage = 0;
	char c, c1, c2;
	int count, value, i = 0;
	int ret;

	ret = parseArgs(argc, argv);
	if(ret) {
		error(PARSING_ERR_STR);
		return ret;
	}

	if(dec == 0) {
		info("Start compress...");
		debug("Creating tree...");
		while((c = getChar()) != getEOF()) {
			ret = saveTreeEl(&storage, c, i++);
			if(ret) {
				error(ALLOC_ERR_STR);
				return ret;
			}
		}
		debug("Storing tree into file...");
		saveTree(storage);
		info("File successfully compressed");
	}
	else if(dec == 1) {
		info("Start decompress...");
		while((c = getChar()) != getEOF()) {
			c2 = getChar();
			c1 = getChar();
			count = getIntFromChars(c1, c2);
			value = 0;
			while(count-- > 0) {
				c2 = getChar();
				c1 = getChar();
				value += getIntFromChars(c1, c2);
				moveFilePos(value);
				putChar(c);
			}
		}
		info("File successfully decompressed");
	}
	closeFiles();
	return 0;
}

int parseArgs(int argc, char **argv)
{
	charp fileread = 0, filewrite = 0;
	int argn = argc;
	charp arg;
	extern int dec;

	while(argn-- > 1) {
		arg = argv[argc - argn];
		if(*arg == '-') {
			switch(*++arg) {
				case 'd': {
					setDebugLevel(++arg);
					break;
				}
				case 'r': {
					dec = 1;
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
	debug("Files: \"%s\", \"%s\"", fileread, filewrite);
	openFileRead(fileread);
	openFileWrite(filewrite);
	return 0;
}

int saveTree(treep t) {
	intchainp p;
	int diff, pvalue = 0;
	if(t != 0) {
		saveTree(t->left);
		putChar(t->value);
		putChar(getCharFromInt2(t->count));
		putChar(getCharFromInt1(t->count));
		p = t->pos;
		while(p) {
			diff = p->value - pvalue;
			putChar(getCharFromInt2(diff));
			putChar(getCharFromInt1(diff));
			pvalue = p->value;
			p = p->next;
		}
		saveTree(t->right);
	}
	return 0;
}
