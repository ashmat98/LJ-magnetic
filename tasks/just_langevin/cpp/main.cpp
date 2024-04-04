// #define EIGEN_USE_BLAS
// #define EIGEN_USE_MKL_ALL

#include <iostream>
#include "langevin.h"


using namespace std;

int main(int argc, char *argv[]){

    char * pEnd;

    langevin(
        argv[1],
        strtol(argv[2], &pEnd, 10));


    return 0;
}