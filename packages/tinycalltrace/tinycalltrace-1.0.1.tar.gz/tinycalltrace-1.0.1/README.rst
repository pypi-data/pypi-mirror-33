Overview
========

Trace function call , and generate call tree graph which is sutable for
using vim.

Using this module, understanding large python module is more easier.

Instalation
===========

::

        pip install tinycalltracer

Usage
=====

Simply add following code in the file defined ‘**main**’,

::

   from tinycalltrace import TinyCallTrace

   if __name__ == '__main__':
            TinyCallTrace()

And run your scripts, call tree graphs generate in trace-0xXXXXXXX.txt
file in your current directory. Thease files are call tree graph of each
threads.

This call tree graphs are sutable for examination using vim fold mode.
You can open thease file with vim, and simply type

::

   :set foldmethod=mark

then you can see folded call tree graph. It is so helpful to understand
call graph, easy to search specified function call/caller.

And also with vim ‘goto file command’ on a line of call tree graph, you
can easily examin source code of call/caller.

Enjoy!
