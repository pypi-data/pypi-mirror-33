prs
===

prs is a small utility that lets you pipe things to Python and process them in a list comprehension.

If you've ever wished you could manipulate items in your shell with a Python list comprehension, prs is for you.


Installation
------------

Just `pip install prs`.


Usage
-----

prs is simple. You pipe stuff into it from the shell, it exposes whatever is piped as a list called `i` (without final
newlines) to a script, and expects the script to return either a string or an iterable to a variable called `o`. That
variable is then printed to stdout, so you can pipe it to `sh` for execution.

```bash
$ ls -1
LICENSE
prs/
README.md
setup.cfg
setup.py

$ ls -1 | prs "o = [l.lower() for l in i]"
license
prs
readme.md
setup.cfg
setup.py
```

Multiple lines can be separated by a semicolon.

Various libraries are already imported (but feel free to import your own):

* os
* sys
* pathlib.Path


Examples
--------

Note: The examples here won't actually run the commands, they will just display them so you can see what will actually
run. To run the commands for real, just append `| sh` to each example.

Append `.bak` to all files in the current directory:

```bash
$ ls -1 | prs "o = ['mv {} {}.bak'.format(l, l) for l in i if Path(l).is_file()]"
mv LICENSE LICENSE.bak
mv README.md README.md.bak
mv setup.cfg setup.cfg.bak
mv setup.py setup.py.bak
```


Concatenate all entries into one:

```bash
02:28:39 $ ls -1 | prs "o = 'touch ' + ' '.join(i)"
touch LICENSE prs README.md setup.cfg setup.py
```


Completely ignore all input:

```bash
02:29:35 $ ls -1 | prs "o = 'hi'"
hi
```
