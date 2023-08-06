#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gdg.h"

char* edge_chars[27];
int edge_index = 0;

List newList(char* str, List next) {
    List self = (List)malloc(sizeof(struct GADDAG_Struct));

    self->str = strdup(str);
    self->next = next;

    return self;
}

Edge newEdge(char* ch, Node node) {
    Edge self = (Edge)malloc(sizeof(struct Edge_Struct));

    self->ch = ch;
    self->node = node;
    self->next = NULL;

    return self;
}

Edge find_edge(Node node, char ch) {
    Edge edge = node->edges;
    while (edge) {
        if (*edge->ch == ch) {
            return edge;
        }
        edge = edge->next;
    }
    return NULL;
}

Node follow_edge(Node node, char ch) {
    Edge edge = find_edge(node, ch);
    if (edge) {
        return edge->node;
    } else {
        return NULL;
    }
}

void set_edge(Node node, char ch, Node dst) {
    Edge edge = find_edge(node, ch);
    if (edge) {
        if (dst->end != edge->node->end) {
            dst->end = 1;
        }
        edge->node = dst;
    } else {
        char* c = NULL;
        for (int i = 0; i < edge_index; ++i) {
            if (ch == *edge_chars[i]) c = edge_chars[i];
        }
        if (!c) {
            c = malloc(sizeof(char));
            *c = ch;
            edge_chars[edge_index++] = c;
        }
        Edge new_edge = newEdge(c, dst);

        if (!node->edges) {
            node->edges = new_edge;
        } else {
            new_edge->next = node->edges;
            node->edges = new_edge;
        }
    }
}

Node add_edge(Node node, char ch, Node dst) {
    Edge edge = find_edge(node, ch);
    if (edge) {
        free(dst);
        return edge->node;
    } else {
        set_edge(node, ch, dst);
        return dst;
    }
}

void add_end(Node node, char ch) {
    Edge edge = find_edge(node, ch);
    if (edge != NULL) {
        edge->node->end = 1;
    } else {
        add_edge(node, ch, newNode(NULL, 1));
    }
}

Node newNode(Edge edges, int end) {
    Node node = (Node)malloc(sizeof(struct Node_Struct));

    node->edges = edges;
    node->end = end;

    return node;
}

List _crawl(Node node, char* partial_word, int wrapped, List cell, int just_wrapped) {
    size_t len = strlen(partial_word);

    if (node->end && !just_wrapped) {
        if (!cell) {
            cell = newList(partial_word, NULL);
        } else {
            cell = newList(partial_word, cell);
        }
    }

    Edge edge = node->edges;
    while (edge) {
        if (*edge->ch == '+') {
            cell = _crawl(edge->node, partial_word, 1, cell, 1);
        } else {
            char* new_partial_word = malloc(len + 2);

            if (wrapped) {
                strcpy(new_partial_word, partial_word);
                new_partial_word[len] = *edge->ch;
                new_partial_word[len + 1] = '\0';
            } else {
                *new_partial_word = *edge->ch;
                strcpy(new_partial_word + 1, partial_word);
            }

            cell = _crawl(edge->node, new_partial_word, wrapped, cell, 0);
            free(new_partial_word);
        }
        edge = edge->next;
    }

    return cell;
}

List _crawl_end(Node node, char* partial_word, List cell) {
    size_t len = strlen(partial_word);

    if (node->end) {
        if (!cell) {
            cell = newList(partial_word, NULL);
        } else {
            cell = newList(partial_word, cell);
        }
    }

    Edge edge = node->edges;
    while (edge) {
        if (*edge->ch != '+') {
            char* new_partial_word = malloc(len + 2);

            *new_partial_word = *edge->ch;
            strcpy(new_partial_word + 1, partial_word);

            cell = _crawl_end(edge->node, new_partial_word, cell);
            free(new_partial_word);
        }
        edge = edge->next;
    }

    return cell;
}
