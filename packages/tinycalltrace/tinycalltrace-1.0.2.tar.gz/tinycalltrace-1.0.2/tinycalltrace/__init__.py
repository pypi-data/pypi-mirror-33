# 
# -*- encoding: utf-8 -*-
#
# Copyright 2018 Takahide Nojima
# 
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files 
# (the "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import threading

__version__ = '1.0.0'

class _TraceByAThread:
    def __init__(self,thread_id):
        self._fname = "trace-"+str(thread_id)+".txt"
        try:
            self._f = open(self._fname,"wb",buffering=0)
        except:
            self._f = sys.stdout
        self._depth = 0

    def __del__(self):
        if self._f != sys.stdout:
            self._f.close()
            print("{} is closed\n".format(self._fname))

class TinyCallTrace:
    def __init__(self):
        self._trace_pool = dict()
        threading.settrace(self.trace_dispatch)
        sys.settrace(self.trace_dispatch)

    def trace_dispatch(self, frame, event, arg):
        thread_id = hex(threading.get_ident())
        if not (thread_id in self._trace_pool):
            self._trace_pool[thread_id] = _TraceByAThread(thread_id)
        trace_info = self._trace_pool[thread_id]
        co = frame.f_code
        if event == 'call':
            prev_space = "  " * trace_info._depth
            output_str="{}->{}: {}:{} ".format(prev_space,co.co_name,
                    co.co_filename,frame.f_lineno)
            fback = frame.f_back
            fback_fname = 'None'
            fback_lineno ='None'
            if hasattr(fback,'f_code') :
                fback_fname = fback.f_code.co_filename
            if hasattr(fback,'f_lineno'):
                fback_lineno = fback.f_lineno
            output_str += "from {}:{} ".format(fback_fname,fback_lineno)
            output_str += "{{{\n"
            trace_info._f.write(output_str.encode())
            trace_info._depth += 1

        if event == 'return':
            trace_info._depth -= 1;
            prev_space = "  " * trace_info._depth
            output_str="{}<-{}: {}:{} ".format(prev_space,co.co_name,
                    co.co_filename,frame.f_lineno)
            output_str += "}}}\n"
            trace_info._f.write(output_str.encode())

        return self.trace_dispatch
