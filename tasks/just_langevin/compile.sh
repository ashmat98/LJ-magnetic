#!/usr/bin/env bash

g++ -Wall -shared -std=c++14 -fPIC \
$(python3 -m pybind11 --includes) \
-I/home/ashmat/.local/include \
./cpp/bind.cpp \
-o langevin$(python3-config --extension-suffix)




# -I/home/ashot/eigen/  \
# -I/home/ashot/pybind11/include  \
# -L/home/ashot/miniconda3/lib \

# `python3.9-config --ldflags` \
# -lpython3.9 \

# $ c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) example.cpp -o example$(python3-config --extension-suffix)