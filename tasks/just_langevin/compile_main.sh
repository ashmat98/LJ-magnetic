#!/usr/bin/env bash

g++ -Wall -std=c++14 -fPIC -O3 -ffast-math -march=native -DEIGEN_NO_DEBUG \
-I/home/ashmat/.local/include \
./cpp/main.cpp \
-o runme


