# CuReSim-LoRM: a tool to simulate metabarcoding long reads

CuReSim-LoRM (Customized Read Simulator to generate Long Reads for Metabarcoding) is a tool which generates
synthetic long sequencing reads for metabarcoding. CuReSim-LoRM is developed in Java and is distributed as an
executable jar file.

# Table of Contents
* [Installation](#Installation)
* [Usage](#Usage)
* [Methods](#Methods)
* [Training error models](#Learning-error-models)
* [External tolls](#External-tools)
* [Support](#support)
* [Citation](#citation)

# Installation

CuReSim-LoRM does not need installation step but require Java installed on your machine
(see http://www.oracle.com/us/technologies/java/overview/index.html for more details on Java).

To run CuReSim-LoRM, use the following command line :

```java -jar CuReSim-LoRM.jar [options] -f <input_file> [options]```

For big datasets you can use the ”java -XmxYYg” argument to allocate more memory to CuReSim (e.g. -Xmx20g to
allocate 20Gb of RAM).

# Usage
```
Usage: java -jar simulator.jar [options] -f <input_file> [options]
-f file_name 	 [mandatory] reads fastq file (without errors, can be obtained form Grinder)
-o file_name 	 [facultative] name of output fastq file [output.fastq]
-r int 	 [facultative] number of random reads [0]
-q char 	 [facultative] quality encoding character [')']
-p file_name 	 [facultative] error profile
-para int[6] 	 read length parameters
-h 	 print this help
```

# Methods 
see pdf

# Training error models
The python script, train_CuReSim-LoRM.py, was developed to automate the whole process, computing the parameters and running CuReSim-LoRM.

![Pipeline](docs/figure1_ter.png)

# External tools
## Grinder

## minimap2

## bbmap



# Support
For questions and comments, please contact us at segolene.caboche(AT)univ-lille.fr.

# Citation

A manuscript describing CuReSim-LoRM is under publication. If you make use of the CuReSim-LoRM, please cite us: Caboche et al., CuReSim-LoRM: a tool to simulate metabarcoding long reads (submited).
