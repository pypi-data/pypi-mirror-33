#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gdg.h"
#include "cgaddag.h"

void add_word(GADDAG gdg, char* word) {
    size_t l = strlen(word);
    char word_arr[l + 1];
    word_arr[l] = '\0';
    strncpy(word_arr, word, l);

    gdg->length++;

    // Add path from last letter in word
    Node node = gdg->root;
    for (int i = l - 1; i > 0; --i) {
        node = add_edge(node, word_arr[i], newNode(NULL, 0));
    }
    add_end(node, word_arr[0]);

    if (strlen(word) == 1) return;

    // Add path from penultimate letter in word
    node = gdg->root;
    for (int i = l - 2; i >= 0; --i) {
        node = add_edge(node, word_arr[i], newNode(NULL, 0));
    }
    node = add_edge(node, '+', newNode(NULL, 0));
    add_end(node, word_arr[l - 1]);

    // Create remaining paths
    for (int m = l - 3; m >= 0; --m) {
        Node existing_node = node;
        node = gdg->root;
        for (int i = m; i >= 0; --i) {
            node = add_edge(node, word_arr[i], newNode(NULL, 0));
        }
        node = add_edge(node, '+', newNode(NULL, 0));
        set_edge(node, word_arr[m + 1], existing_node);
    }
}

int has(GADDAG gdg, char* word) {
    size_t l = strlen(word);
    char word_arr[l];
    strncpy(word_arr, word, l);

    Node node = gdg->root;

    for (int i = l - 1; i >= 0; --i) {
        node = follow_edge(node, word_arr[i]);
        if (!node) return 0;
    }

    if (node->end) return 1;
    else return 0;
}

List contains(GADDAG gdg, char* sub) {
    size_t l = strlen(sub);
    char sub_arr[l];
    strncpy(sub_arr, sub, l);

    Node node = gdg->root;

    for (int i = l - 1; i >= 0; --i) {
        node = follow_edge(node, sub_arr[i]);
        if (!node) return NULL;
    }

    return _crawl(node, sub, 0, NULL, 0);
}

List starts_with(GADDAG gdg, char* prefix) {
    size_t l = strlen(prefix);
    char prefix_arr[l];
    strncpy(prefix_arr, prefix, l);

    Node node = gdg->root;

    for (int i = l - 1; i >= 0; --i) {
        node = follow_edge(node, prefix_arr[i]);
        if (!node) return NULL;
    }

    node = follow_edge(node, '+');
    if (!node) return NULL;

    return _crawl(node, prefix, 1, NULL, 0);
}

List ends_with(GADDAG gdg, char* suffix) {
    size_t l = strlen(suffix);
    char suffix_arr[l];
    strncpy(suffix_arr, suffix, l);

    Node node = gdg->root;

    for (int i = l - 1; i >= 0; --i) {
        node = follow_edge(node, suffix_arr[i]);
        if (!node) return NULL;
    }

    return _crawl_end(node, suffix, NULL);
}

GADDAG newGADDAG() {
    GADDAG gdg = (GADDAG)malloc(sizeof(struct GADDAG_Struct));

    gdg->root = newNode(NULL, 0);
    gdg->length = 0;

    return gdg;
}
