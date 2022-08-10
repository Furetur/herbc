#include <stdio.h>

void print_int(int i) {
    printf("%d", i);
}

void print_bool(char b) {
    if (b == 0) {
        printf("false");
    } else {
        printf("true");
    }
}

void print_str(char* s) {
    printf("%s", s);
}
