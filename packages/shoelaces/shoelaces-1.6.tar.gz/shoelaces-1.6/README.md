# README #
### Shoelaces ###

This is an open source program for processsing ribosome profiling data written in Python3. Works on Linux and Mac OS.

## INSTALL ##
A minimal install of the packaged version can be done directly from PyPI:
`pip3 install shoelaces`

## RUN ##
To start the window application, run `shoelaces`

To start the console application, run `shoelaces -h`

### Running from source ###
Alternatively, clone the source repo, then run `run.sh` or `run-console.sh`. Make sure you have Python3 packages installed: pysam, numpy, pyqt5, pyopengl.

### DEMO DATASETS ###
Example data (BAM, GTF, XML) are in the `Data` directory.

## GUI ##

![alt text](https://bytebucket.org/valenlab/shoelaces/raw/058a430b398f6a5b1d388403cfaf3851b260d152/shoelaces_GUI.png)

* Load sequence alignment data (BAM format, note that the index BAI file needs to be in the same directory) and gene annotations (GTF format).
* In the 'Resources' window, select one GTF and one BAM file (they will turn blue).
* Press the 'Set Offset' button to create metaplots around transript start and stop per read length. The number of transcripts used for creating metaplots can be adjusted in the drop-down menu (default is top 10% most expressed transcripts).
* The footprint lengths with 3-nucleotide periodicity appear in the 'Common' tab (footprints stemming from translating ribosomes).
* The offsets are calibrated automatically, you can adjust the positions by dragging the plots left/right ('0' in 'Start/Stop codon' plots are the first nucleotides of start/stop codons respectively.
* Export your selected data into WIG format by pressing the 'Export Wig' button (you can either create single file or one per each selected footprint length).

Noise regions can be defined by a separate transcript file. Right click on the desired to resource and select set as noise (it will turn red).

Single transcripts or genes in your current transcript file can be excluded from processing, by right clicking and select toggle usage (they will be grayed out).

To store your current project, select save button. This stores and xml with your current offsets, selected files, disabled transcripts.

In the 'Data Overview' you can click 'Refresh' button to calculate global statistics of your library.
Double-clicking on the gene/transcript names in the panels on the left plots the sequence data in a genome browser-like fashion, with corresponding statistics.

For processing multiple alignment files in the same way, go to File -> Batch... and add BAM files with 'Add' button.

## Console ##
See the `shoelaces -h` for an example.

Using specified offsets (config file):
`shoelaces -t -files Data/offsets.xml Data/example.bam Data/example.gtf out.wig`

Split output for fragment lengths specified in offsets.xml:
`shoelaces -t -s -files Data/offsets.xml Data/example.bam Data/example.gtf out.wig`

Output wiggle in transcript coordinates:
`shoelaces -t -r -files Data/offsets.xml Data/example.bam Data/example.gtf out.wig`

Overwrite fragment lengths for which to create wig output:
`shoelaces -t -lengths 28 29 -files Data/offsets.xml Data/example.bam Data/example.gtf out.wig`

Automatic offset detection:
`shoelaces -a -files Data/example.bam Data/example.gtf out.wig`

Offset detection with using CDS end (stop codon peak):
`shoelaces -a -c -files Data/example.bam Data/example.gtf out.wig`

Print offset plots in the console (from -15 to +15 relative to CDS start)
`shoelaces -a -p -files Data/example.bam Data/example.gtf out.wig`

### Who do I talk to? ###

* Asmund.Birkeland@uib.no