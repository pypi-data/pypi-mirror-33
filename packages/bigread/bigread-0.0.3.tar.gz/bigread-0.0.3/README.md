# BigRead

[![Build Status](https://travis-ci.org/duhaime/big-read.svg?branch=master)](https://travis-ci.org/duhaime/big-read)

In text processing, it is sometimes necessary to read files that are too large to fit into a machine's main memory. In those situations, one must read only a few lines of the file into RAM, then read the next few lines, and so on, this way ensuring that only a small number of lines from the input file are in main memory at any given time. BigRead implements a simple file reader for exactly these situations, to allow machines to read files that are absolutely huge.

## Installation

To install BigRead, just run:

```bash
pip install bigread
```

## Usage

Suppose you have a large file to read into RAM:

```python
with open('large.txt', 'w') as out:
  for i in range(10**6):
    out.write('this is line ' + str(i) + '\n')
```

To read this file with BigRead, import the module and create a stream, then iterate over the stream to read the file lines one-by-one:

```python
from bigread import Reader

stream = Reader(file='large.txt', block_size=10)
for i in stream:
  print(i)
```

This will iterate over each line in the input file, loading `block_size` lines into RAM at any time.

If it's more convenient, you can also read lines from the file one-by-one on demand:

```python
stream = Reader(file='large.txt', block_size=100)
print( stream.next() ) # prints the first line in the text
print( stream.next() ) # prints the second line in the text...
```
