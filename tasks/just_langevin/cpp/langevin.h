#ifndef LANGEVIN_H
#define LANGEVIN_H 1

#define FILE_EXTENSION ".bin"
#define SEP "/"

#define  sq(x) (x)*(x)

#include <Eigen/Dense>
#include <tuple>
#include <fstream>
#include <iostream>
#include <ctime>

#include "myrandom.h"
#include "utils.h"

using namespace std;

ofstream create_dumpfile(string name="") {
    if (name == "") {
        name = "dump" + get_time_string();
    }
    string path = string("/data/biophys/ashmat/LJ-magnetic/") + "dumps" + SEP + name + FILE_EXTENSION;
    cout<<path<<endl;
    
    ofstream dump_file;
    
    dump_file.open(path, ios::out | ios::binary);
    assert(dump_file.is_open());
    //////////////
    return dump_file;
}



const double dt = 0.01;
const double gamma_ = 0.003;
const double eps = 3.6e-4;
const double a = 0.2;
const int N = 500;
const int N_output = 500;

const double N_inv = 1. / N;
const double ma_tau=50;
const double ma_alpha = 1-0*exp(- dt/ ma_tau);
const double E1 = 1;
const double Omega0 = 0.8 * a;

int dump_every = 200;
int warmup_steps = int(1./gamma_/dt * 100);




void langevin(string dump_name, int time_interval){
     int steps = 1.0 * time_interval / dt;
     /* warmup_steps=0; */

     Eigen::Matrix3Xd new_x;
     Eigen::Matrix3Xd new_v;
     
     auto dump_file = create_dumpfile(dump_name);
     dump_file.write((char*)&N_output, 4);


     Eigen::Vector<double, N> x,y,z,vx,vy,vz;
     x.setZero();
     y.setZero();
     z.setZero();
     vx.setZero();
     vy.setZero();
     vz.setZero();


     double Omega = Omega0;
     double L = E1 * 2 * Omega / (3 * sq(a) - sq(Omega) );
     double ax = a, ay = a, az = 4*a;
     double T, root_T;
     double root_2gamma_dt = sqrt(2 * dt * gamma_);
     double t = 0;
     double h = 0;


     randn rmg(N,1);

     int percent = 1;
     int max_precent = 1000;

     time_t last_time = time(NULL);
     // cout << ma_alpha << endl;
     for (int step=-warmup_steps; step<steps;++step){

          if (step == 0){
               ax = a * (1+eps), ay = a * (1-eps), az = 4*a;
               percent = 1;
               t=0;
          }

          // L += 

          Omega += 0.5 * sq(3 * sq(a) - sq(Omega) ) / (E1 * (3 * sq(a) + sq(Omega)) ) * 
               4 * eps * sq(a) * h * dt * (step>=0);
          L = E1 * 2 * Omega / (3 * sq(a) - sq(Omega) );
          
          // Omega = E1 / L * (sqrt(1 + 3 * sq(a) * sq(L) / sq(E1)) - 1);

          T = E1 * ( sq(a) - sq(Omega)) / (3 * sq(a) - sq(Omega));
          root_T = sqrt(T);


          vx += (- gamma_ * (vx+Omega * y)   - sq(ax) * x ) * dt
               + root_2gamma_dt * root_T * rmg();
          vy += (- gamma_ * (vy-Omega * x) - sq(ay) * y) * dt
                + root_2gamma_dt * root_T * rmg();
          vz += - gamma_ * vz * dt - sq(az) * z 
               + root_2gamma_dt * root_T * rmg();


          x += vx * dt;
          y += vy * dt;
          z += vz * dt;
          

          h = x.dot(y) * N_inv * ma_alpha + h * (1- ma_alpha);

          // L += 4 * eps * sq(a) * h * dt;

          t += dt;

          if (step >= 0 && step % dump_every == 0){
               double dstep = step;

               dump_file.write((char*)&dstep, 8);
               dump_file.write((char*) &t , 8);
               dump_file.write((char*) &Omega , 8);
               dump_file.write((char*) &T , 8);
               dump_file.write((char*) &L , 8);


               dump_file.write((char*) x.data(), N_output*8);
               dump_file.write((char*) y.data(), N_output*8);
               dump_file.write((char*) z.data(), N_output*8);
               dump_file.write((char*) vx.data(), N_output*8);
               dump_file.write((char*) vy.data(), N_output*8);
               dump_file.write((char*) vz.data(), N_output*8);
          }
          if (step<0 && (warmup_steps+step) > 0.01 * percent * warmup_steps){
               time_t current_time = time(NULL);
               int delta_t = current_time - last_time;
               last_time = current_time;
               printf("warmup %d%%  %s  ~%d min left\n", percent, 
                    get_time_string().c_str(),
                         int((100. - percent) * delta_t *1.0 /60)
                    );
               percent++;
          }
          if (step  > (1./max_precent) * percent * steps ){
               time_t current_time = time(NULL);
               int delta_t = current_time - last_time;
               last_time = current_time;
               printf("%0.1f%%  %s  ~%d min left\n", percent * 100./max_precent, 
                    get_time_string().c_str(),
                         int((max_precent - percent) * delta_t * 1.0 /60)
                    );
               percent++;
          }
     }
}




#endif
