#include <pybind11/pybind11.h>
#include <Eigen/Dense>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include <vector>
#include <random>

#include "langevin.h"


using namespace std;
namespace py = pybind11;
using namespace pybind11::literals;

int add(int i, int j) {
    return i + j;
}
PYBIND11_MODULE(langevin, m) {
    m.doc() = "Transient Numerical solution"; 
    
    m.def("add", &add, "A function which adds two numbers");

    // m.def("sigma_1", &Sigma_1, "first order approximation of Sigma",
    //     "t"_a, "Sigma0"_a, "Omega"_a,  "ax"_a, "ay"_a, "gamma"_a, "T"_a
    //     , py::return_value_policy::reference_internal
    // );
}