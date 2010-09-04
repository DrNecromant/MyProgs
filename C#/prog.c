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
