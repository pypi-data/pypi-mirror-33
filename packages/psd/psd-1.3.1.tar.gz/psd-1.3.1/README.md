# PSD Module


**This module provides easy-to-use tools for quick data visualization and spectral
analysis.**

Data must be stored on text, Numpy or HDF5 files, and all formats compatible with
the standard `numpy.loadtxt` and `numpy.load` are accepted. First dimension, or
rows, is used for time and second dimension, or columns, for series. The first
column is always assumed to represent the times associated with each row.

## Installation

Make sure that Python 3 is available on your machine, and run

```shell
pip3 install psd
```

The package is also available at https://pypi.org/project/psd/.

## Getting Started

### Time-Series Visualization

You can visualize time-series from Numpy or text files using

```shell
psd --time-series my_file.npy another_file.txt ...
```

You can read HDF5 files as well by specifying the path to the dataset inside
your file using

```shell
psd --time-series my_hdf5_file.hdf5:mygroup/mydataset ...
```

### Power Spectrum Estimation

To compute Power Spectral Density (PSD) estimates for each series using the
[Welch method](https://en.wikipedia.org/wiki/Welch%27s_method), simply use

```shell
psd my_file.npy
```

You can specify the number of rows at the top of the files you want to skip
using `-s SKIPROWS` option, the number of points per segment you want to use
with `-n NPERSEF` option, or the windowing function using `--window WINDOW`.

For time-series visualization and spectral analysis, you can hide the legend
with the `--no-legend` option, specify a title with `--title TITLE`, or save
the output as a text file, a Numpy file or an image using `-o OUTPUT`. You
can specify line and marker aspect using matplotlib notation with `--aspect`.

```shell
psd -s 500 -n 10000 --window nuttall my_file.npy --title "This is an example"
```

### Format Conversion

You can easily convert from text files to Numpy binary files using the quick
`convert` command-line tool included in this package, i.e.

```shell
convert my_file1.txt my_file2.text
```

To reverse the conversion and get a text file from a Numpy file, use the `-r`
option. You can specify the output file name using `-o OUTPUT`.

```shell
convert -r my_numpy.npy -o my_text_file.txt
```

The tool can also remove original files as soon as they are converted if you
specify the `--delete` or `-d` option.

```shell
convert -d file*.txt
```

## Documentation

Other options are available, use `psd --help` or `convert --help` to show
documentation.

Developped by Jean-Baptiste Bayle (APC/CNES/CNRS), bayle@apc.in2p3.fr.
