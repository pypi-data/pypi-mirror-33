#include "stdio.h"
#include "stdlib.h"
#include "cbuffer.h"

void print_info(CBuffer *buff){
    printf("offset %s %zd\n","size", sizeof(CBuffer));

    printf("%-15s: %zd\n","base"       ,  buff->base);
    printf("%-15s: %zd\n","size"       ,  buff->size);
    printf("%-15s: %zd\n","size_header",  buff->size_header);
    printf("%-15s: %zd\n","size_slots" ,  buff->slots[0]);
    printf("%-15s: %zd\n","size_objects" ,buff->objects[0]);
    printf("%-15s: %zd\n","size_pointers",buff->pointers[0]);
    printf("%-15s: %zd\n","size_garbage" ,buff->garbage[0]);
};




