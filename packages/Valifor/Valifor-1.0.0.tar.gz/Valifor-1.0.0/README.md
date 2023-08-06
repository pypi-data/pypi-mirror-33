
Valifor
=============================

__Valifor__ is a small easily extensible command line tool to validate different NGS file formats.
Currently the following file formats are supported:
* Fasta
* Fastq

Motivation
======================

In any data driven workflow the quality of the data is of high importance. Especially with formats that get can be manually modified there is a chance for corrupted files that don't fit the format anymore. 
If corrupted files are able to enter the workflow undetected the whole system can break and may have to be reset, even if it doesn't break the result gotten at the end will not be usable and all the work done will have to be repeated.
In the second case you may get an even worse situation if the mistake is not found quickly. All further work and conclusions building on the corrupted result might also be unusable. 

To combat this situation there are validators for different formats that are able to make sure they conform to all the defined rules. For example there is [FastaValidator](https://github.com/jwaldman/FastaValidator) and the [FastqValidator](https://github.com/statgen/fastQValidator) which both can validate their respective formats. There are also programs that not only validate certain formats but also allow to run analysis on them like [bamUtil](https://github.com/statgen/bamUtil)

Yet there are no tools that concentrate on validating a broad range of formats that would allow to have a single program that validates all of the different files going into a workflow. Instead currently it is needed to have multiple tools which all need to be maintained.   

In order to address this issue we started creating *valifor* a command line application that will be able to validate different NGS file formats while it's currently a small start, it's easily extensible and a needed format can quickly be added.

Table of Contents
=======================

* [The overall architecture](#toa)
* [Installation](#install)
* [The command line interface](#cli)
* [Adding a new Format](#addFormat)

<a name="toa">The overall architecture </a>
=======================
The *valifor* architecture is shown in the following graph: 

![valifor](https://user-images.githubusercontent.com/35918514/42245707-01840510-7f1a-11e8-8860-20ea51f056b9.jpg)


The basic structure is the factory pattern.

Following the flow of information the command line interface receives the input of one ore multiple paths to files/directories to validate and optionally the format which it should check.
This is used to start the validation process in the main logic. There the factory is used to get the correct validator for the needed format from the child-classes of AbsValidator.
The AbsValidator is the base class for all implemented validators. Each of the child-classes has to implement the interface given in the parent. 
The validator given by the factory is then used to validate the files and it returns information about if the files are valid and if not where the format is broken. 


<a name="install">Installation </a>
=======================
You can install *valifor* using the source files found on [Github](https://github.com/qbicsoftware/dmqb-grp1-2018)

After you downloaded the directory you can call:
    
    $ pip install path_to_the_directory

to install it on your system.


<a name="cli">Using Valifor: </a>
========================

Once *valifor* is installed, it can be used. 
You can get an overview on how to use it by adding the  ``--help`` option in the command line. It will show an overview and explanation for *valifor*:

    $ valifor --help
    Usage: valifor [OPTIONS] [PATHS]...

    Welcome to the format validator Valifor:

    Valifor is a easily extensible validator for different formats. To get
    started you can call "valifor --help" to get this message again and more
    information to the options.

    To use valifor you can call:

           "valifor [path_to_file]" to check its format based on its
           file-ending.

           "valifor [path_to_file] --format [format]" to check its format
           based on the given format.

	Options:
	  -f, --format [fasta-dna|fasta-aa|fastq]
	                                  Type of format to be tested for all given files
	  -h, --help                      Show this message and exit.

you can also test whole directories by giving the path to the directory:

    $ valifor [path_to_dir]

or test multiple files and/or directories:

    $ valifor [path_to_dir] [path_to_file]


#### An example use case: 

To use *valifor* to validate a fasta file call:

    $ valifor  example.fasta --format fasta-dna
    
Then it prints the result in the command line. In case of a valid file it prints the format tested and the name:

    $ valid: example.fasta - fasta-dna

or in case of a corrupted file it additionally returns the reason if it is possible:

    $ failed: example.fasta - fasta-dna: Character [O] not allowed in sequence. At line: 3:10

if the file or directory doesn't exist it prints a warning with the full path: 

    Given path does not exist: /path/to/fileOrDir

    
<a name="addFormat">Adding a new Format: </a>
=======================
 
To add a new format you have to write a corresponding validator of course. 
The new plug-in must consist of a class that inherits from the AbsValidator and overwrites all its functions following the description in the documentation of AbsValidator.
(Additionally there should be a unittest-class with test-files.)

With the new validator-class most of the work is finished the only thing left is to integrate it in the project.
For this you only need add it in the functions of the validator-factory which is also in the validator module.

You will find 4 functions:

* available_formats(): 
	* add the new name which the option in the CLI should have. 
* get_format_from_ending(file_ending):
	* add the conversion from the file-ending to the name of the option.
* get_validator(name):
	* add the new class as a return for the new option.
* def get_uncertain_endings():
	* if the file-ending is not enough to be completely certain about the exact format also add it here. 

And with that you are finished and have integrated a new format for this project.



