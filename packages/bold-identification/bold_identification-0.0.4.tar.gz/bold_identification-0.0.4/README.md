# bold_identification

## 1 Introduction
This is a package which can get the taxonomy information of sequences from BOLD [http://www.boldsystems.org/index.php](http://www.boldsystems.org/index.php).

To get the taxonomy information of a sequence from BOLD, what we usually do is: (1) open the website `http://www.boldsystems.org/index.php/IDS_OpenIdEngine` with a browser; (2) Choose a database; (3) input the sequence (4) click `submit` and wait for the result. (5) Copy the taxonomy information from the result page.

`bold_identification` actually does the same things as above, but it does such a thing automatically for you, and makes life easily.


Currently, `bold_identification` only runs on Mac OS, Windows 64bit, Linux.

But be ware, only the Chrome browser works on Windows, but FireFox doesn't.

## 2 Installation

    pip3 install bold_identification-X.X.X.tar.gz

There will be a command `bold_identification` created under the same directory as your `pip3` command.

## Usage
run `bold_identification`


    usage: bold_identification [-h] -i INFILE -o OUTFILE
                               [-d {COX1,COX1_SPECIES,COX1_SPECIES_PUBLIC,COX1_L640bp,ITS,Plant}]
                               [-b {Firefox,Chrome}] [-t TIMEOUT]

    To identify taxa of given sequences. If some sequences fail to get taxon
    information, you can run another searching for those sequences. This can be
    caused by TimeoutException if your network to the BOLD server is bad. Or you
    can lengthen the time to wait for each query (-t option). By
    mengguanliang@genomics.cn.

    optional arguments:
      -h, --help            show this help message and exit
      -i INFILE             input fasta file
      -o OUTFILE            outfile
      -d {COX1,COX1_SPECIES,COX1_SPECIES_PUBLIC,COX1_L640bp,ITS,Plant}
                            database to search [COX1]
      -b {Firefox,Chrome}   browser to be used [Firefox]
      -t TIMEOUT            the time to wait for a query [30]









