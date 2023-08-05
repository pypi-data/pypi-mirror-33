decol
=====

[![Build Status](https://travis-ci.org/ctberthiaume/decol.svg?branch=master)](https://travis-ci.org/ctberthiaume/decol)

A tool to drop or keep columns from a CSV file.

### Features
* columns can be specified as 1-based integer indexes or column headers
* multiple indexes or headers can be specified as a comma-separated list
* negative indexes are supported
* index ranges are also supported, e.g. 1:2 for the first two column


### Usage
```
$ decol -h
Usage: decol [OPTIONS] INPUT OUTPUT

  A tool to drop or keep columns from a CSV file.

Options:
  -c, --columns COLUMNS       Comma-separated list of 1-based column indexes
                              to remove. Negative integers will index from the
                              end. May use a range, e.g. 1:2 or -3:-2 for
                              first and second of three columns. Ranges must
                              always be given in left to right column order
                              for both positive and negative indexes. Mutually
                              exclusive with --headers.
  -H, --headers HEADERS       Comma-separated list of columns to remove by
                              first-line header. Mutually exclusive with
                              --columns.
  -s, --sep SEPARATOR         Column separator.  [default: ,]
  -o, --output-sep SEPARATOR  Output column separator. [default: --sep value]
  --keep                      Keep only the specified columns in the order
                              specified in --columns or --headers.  [default:
                              False]
  --version                   Show the version and exit.
  -h, --help                  Show this message and exit.
```
