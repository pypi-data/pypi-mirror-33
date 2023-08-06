# PSL TA1 Implementations
This code base contains the code to create TA1 primities that contain PSL solutoions to 
common modelling problems.


## Building & Submitting the docker images:
1. The following must be located in the docker folder before the docker image is built:
    - PSL Jar: Canary jars can be found at ```https://linqs-data.soe.ucsc.edu/maven/repositories/psl-releases/org/linqs/psl-cli/CANARY/```
    - primitive-interfaces: git@gitlab.datadrivendiscovery.org:d3m/primitive-interfaces.git
    - types: git@gitlab.datadrivendiscovery.org:d3m/types.git

2. cd to the docker directory and run the following command. The label ensures that the image is registered against 
the correct docker ci project in the d3m gitlab ```docker build -f Dockerfile -t registry.datadrivendiscovery.org/ta1/sri_ta1:latest .```

3. 

## Implementations
### Graph completion:
