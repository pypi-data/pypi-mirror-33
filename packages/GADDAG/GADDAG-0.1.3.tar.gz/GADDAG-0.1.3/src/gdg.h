#ifndef GDG_H_INCLUDED
#define GDG_H_INCLUDED
typedef struct Edge_Struct* Edge;
typedef struct Node_Struct* Node;
typedef struct GADDAG_Struct* GADDAG;
typedef struct List_Struct* List;

struct Edge_Struct {
    char* ch;
    Node node;
    Edge next;
};

struct Node_Struct {
    Edge edges;
    int end;
};

struct List_Struct {
    char* str;
    List next;
};

struct GADDAG_Struct {
    Node root;
    int length;
};

Edge newEdge(char*, Node);

Edge find_edge(Node, char);
Node follow_edge(Node, char);
void set_edge(Node, char, Node);
Node add_edge(Node, char, Node);
void add_end(Node, char);
Node newNode(Edge, int);

List _crawl(Node, char*, int, List, int);
List _crawl_end(Node, char*, List);
#endif
