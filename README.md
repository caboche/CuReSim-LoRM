# CuReSim-LoRM: a tool to simulate metabarcoding long reads

CuReSim-LoRM (Customized Read Simulator to generate Long Reads for Metabarcoding) is a tool which generates
synthetic long sequencing reads for metabarcoding. CuReSim-LoRM is developed in Java and is distributed as an
executable jar file.

# Table of Contents
* [Installation](#Installation)
* [Usage](#Usage)
* [Methods](#Methods)
* [Content description](#content-description)
* [Support](#support)
* [Citation](#citation)

# Installation


CuReSim-LoRM does not need installation step but require Java installed on your machine
(see http://www.oracle.com/us/technologies/java/overview/index.html for more details on Java).

To run CuReSim-LoRM, use the following command line :

```java -jar CuReSim-LoRM.jar [options] -f <input_file> [options]```

For big datasets you can use the ”java -XmxYYg” argument to allocate more memory to CuReSim (e.g. -Xmx20g to
allocate 20Gb of RAM).

# Support
For questions and comments, please contact us at segolene.caboche(AT)pasteur-lille.fr.

# Citation

A manuscript describing MICRA is under publication. If you make use of the MICRA pipeline, please cite us:
Caboche et al., Fast characterization of microbial genomes from high-throughput sequencing data (submited). 
