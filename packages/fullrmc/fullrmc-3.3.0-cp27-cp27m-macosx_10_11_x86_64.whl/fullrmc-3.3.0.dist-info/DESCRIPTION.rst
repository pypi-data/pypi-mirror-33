FUndamental Library Language for Reverse Monte Carlo or fullrmc is a molecular/atomic stochastic fitting platform to reverse modeling experimental data. 
fullrmc is not a standard RMC software but exceeds in its capabilities and functionalities traditional RMC and Metropolis-Hastings algoritm. 
Therefore RMC appellation in fullrmc, is not accurate but it's retained to respecting the community terminology. 
RMC is probably best known for its applications in condensed matter physics and solid state chemistry. 
RMC is used to solve an inverse problem whereby an atomic model is adjusted until its atoms position have the greatest consistency with a set of experimental data.
fullrmc is a python package with its core and calculation modules optimized and compiled in Cython. 
fullrmc's Engine sub-module is the main module that contains the definition of 'Engine' which is the main and only class used to launch the stochastic calculation. 
Engine reads only Protein Data Bank formatted atomic configuration files '.pdb' and handles other definitions and attributes. 
Starting from version 1.x.y fitting non-periodic boundary conditions or isolated molecules is added. 
fullrmc >= 1.2.y can be compiled with 'openmp' allowing multithreaded fitting. 
fullrmc >= 2.x.y engine is a single file no more but a pyrep repository. 
fullrmc >= 3.x.y dynamically removing atoms upon fitting is enabled. 

