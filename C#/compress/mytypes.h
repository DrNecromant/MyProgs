typedef char *charp;

struct intchain {
	int value;
	struct intchain *next;
};

typedef struct intchain *intchainp;

struct tree {
	char value;
	int count;
	intchainp pos;
	struct tree *right;
	struct tree *left;
};

typedef struct tree *treep;
