"""
    experipy.grammar
    ~~~~~~~~~~~~~~~~

    This module provides the core elements which compose the Experipy 
    grammar: Executables, Wrappers, Pipelines, and Groups. These 
    elements facilitate specifying programs to execute as well as the 
    files they depend on. 
"""
import re

from .config import Namespace


class Element(object):
    """The Element class forms the grammar's base class.

    Parameters
    ----------
    inputs : list
        A list of strings which are the names of files that the Element 
        relies on for input. These will be copied to the run directory 
        when an Experiment is used to run the Element.
    outputs: list
        A list of strings which are the names of files that the Element 
        is expected to generate as output. These will be copied from the 
        run directory when an Experiment is used to run the Element.
    """

    def __init__(self, inputs=None, outputs=None):
        self._inputs = inputs if inputs else []
        self._outputs = outputs if outputs else []

    def inputs(self):
        """Generator which yields the Element's input files"""
        for item in self._inputs:
            yield item

    def outputs(self):
        """Generator which yields the Element's output files"""
        for item in self._outputs:
            yield item


class Executable(Element):
    """Executable objects should represent a single program and its arguments.

    Parameters
    ----------
    prog : str
        The name of the program executable.
    opts : list
        A list of command line options to pass to the program. Defaults to
        an empty list if not provided.
    wait : bool
        If False, a '&' will be appended to the argument list, indicating to
        the shell that it should background the program instead of blocking
        on it. Defaults to True.
    """

    def __init__(self, prog, opts=None, wait=True, **kwargs):
        super(Executable, self).__init__(**kwargs)
        self.prog = prog
        self.opts = []
        if opts != None:
            self.opts.extend(opts)

        if wait == False:
            self.opts.append("&")

    def __str__(self):
        """Render the Executable as it will appear in the shell script."""
        return "{0} {1}".format(self.prog, " ".join(map(str,self.opts)))


class Wrapper(Executable):
    """Wrapper objects allow specification of a program which wraps another.

    Wrappers are a subclass of Executable which allow specification of 
    programs such as GDB or Valgrind, which wrap around another program 
    to alter or observe its execution.

    Parameters
    ----------
    prog : str
        The name of the program executable.
    opts : list
        A list of command line options to pass to the program. Must 
        minimally contain a string having the value '[[wrapped]]', which 
        indicates where the wrapped executable should be inserted into 
        the wrapping executable's argument list.
    wrapped : experipy.Executable
        The wrapped Executable. Inputs and outputs specified to wrapped 
        will be included in the resultant object's inputs and outputs.
    wait : bool
        If False, a '&' will be appended to the argument list, 
        indicating to the shell that it should background the program 
        instead of blocking on it. Defaults to True.
    """

    def __init__(self, prog, opts, wrapped, **kwargs):
        if not isinstance(wrapped, Executable):
            raise TypeError("wrapped must be an instance of Executable")
        elif "[[wrapped]]" not in opts:
            raise ValueError("opts must contain '[[wrapped]]'")
        
        super(Wrapper, self).__init__(prog, opts, **kwargs)
        self.wrapped = wrapped

    def __str__(self):
        """Render the Wrapper as it will appear in the shell script."""
        return super(Wrapper, self).__str__().replace(
            "[[wrapped]]", str(self.wrapped)
        )
    
    def inputs(self):
        """Generator which yields the Wrapper's input files"""
        seen = set()
        for item in super(Wrapper, self).inputs():
            if item not in seen:
                seen.add(item)
                yield item
        for item in self.wrapped.inputs():
            if item not in seen:
                seen.add(item)
                yield item
    
    def outputs(self):
        """Generator which yields the Wrapper's output files"""
        seen = set()
        for item in super(Wrapper, self).outputs():
            if item not in seen:
                seen.add(item)
                yield item
        for item in self.wrapped.outputs():
            if item not in seen:
                seen.add(item)
                yield item


class Pipeline(Element):
    """Pipeline objects allow specification of pipelined workflows.

    A Pipeline takes one or more Element parts, and joins them with a 
    '|' operator, indicating to the shell that each part should recieve 
    its input from the previous part, and provide its output to the 
    next.

    Parameters
    ----------
    *parts : 
        One or more Executables or Wrappers to be chained together into 
        a pipeline. Inputs and outputs to the individual parts will be 
        included in the Pipeline's inputs and outputs.
    """

    def __init__(self, *parts, **kwargs):
        for part in parts:
            if not isinstance(part, Executable):
                raise TypeError("'{}' is not an instance of Executable".format(part))
       
        super(Pipeline, self).__init__(**kwargs)
        self.parts = parts

    def __str__(self):
        """Render the Pipeline as it will appear in the shell script."""
        return " | ".join(map(str,self.parts))
    
    def inputs(self):
        """Generator which yields the Pipeline's input files"""
        seen = set()
        for item in super(Pipeline, self).inputs():
            if item not in seen:
                seen.add(item)
                yield item
        for part in self.parts:
            for item in part.inputs():
                if item not in seen:
                    seen.add(item)
                    yield item
    
    def outputs(self):
        """Generator which yields the Pipeline's output files"""
        seen = set()
        for item in super(Pipeline, self).outputs():
            if item not in seen:
                seen.add(item)
                yield item
        for part in self.parts:
            for item in part.outputs():
                if item not in seen:
                    seen.add(item)
                    yield item


class Group(Element):
    """Group objects allow specification of Executables to be run in order.

    In the resultant script, a Group's parts will be included one after 
    another, in the order they were specified. Groups should be used 
    when specifying complex experiments involving multiple steps like 
    set up or post-processing, or combined with the wait parameter to 
    Executable to specify programs which should be run concurrently. A
    Group can also be used as a part in another Group.

    Parameters
    ----------
    *parts : 
        One or more Elements to be placed into the script. Inputs and 
        outputs to the individual parts will be included in the Group's
        inputs and outputs.
    """

    def __init__(self, *parts, **kwargs):
        for part in parts:
            if not (isinstance(part, Element)):
                raise TypeError("'{}' is not an instance of Element".format(part))

        super(Group, self).__init__(**kwargs)
        self.parts = parts

    def __str__(self):
        """Render the Group as it will appear in the shell script."""
        return "\n".join(map(str,self.parts))

    def inputs(self):
        """Generator which yields the Group's input files"""
        seen = set()
        for item in super(Group, self).inputs():
            if item not in seen:
                seen.add(item)
                yield item
        for part in self.parts:
            for item in part.inputs():
                if item not in seen:
                    seen.add(item)
                    yield item
    
    def outputs(self):
        """Generator which yields the Group's output files"""
        seen = set()
        for item in super(Group, self).outputs():
            if item not in seen:
                seen.add(item)
                yield item
        for part in self.parts:
            for item in part.outputs():
                if item not in seen:
                    seen.add(item)
                    yield item

