#!/usr/bin/env python
from __future__ import absolute_import, division

"""
optplus: some additional optparse features

add an optparse action to load an option from a file, to add to dicts,
and a type for slices
"""

__version__ = "$Revision$"

# Copyright 2007-2009 Michael M. Hoffman <hoffman+software@ebi.ac.uk>

from collections import defaultdict
from optparse import (Option as _Option, OptionError,
                      OptionGroup as _OptionGroup,
                      OptionParser as _OptionParser, OptionValueError)
import sys

# XXX: replace with itertools.repeat().next, see segway._utils.constant
def _constant(constant):
    def _constant_inner():
        return constant

    return _constant_inner

# adapted from http://docs.python.org/lib/optparse-callback-example-6.html
def optional_arg_callback(option, opt_str, value, parser):
    assert value is None

    done = 0
    value = []
    rargs = parser.rargs

    # Stop if we hit an arg like "--foo", "-a", "-fx", "--file=f",
    # etc.  Note that this also stops on "-3" or "-3.0", so if
    # your option takes numeric values, you will need to handle
    # this.

    # XXX: extract block into a function to reduce spaghetti
    if rargs and rargs[0] and not rargs[0].startswith("-"):
        try:
            # XXX: allow non-float types
            value = float(rargs[0])
            del rargs[0]
        except ValueError:
            value = option.unspecified
    else:
        value = option.unspecified

    setattr(parser.values, option.dest, value)

def str2slice_or_int(text):
    args = [int(x) if x else None for x in text.split(":")]

    if len(args) == 1:
        return args[0]
    else:
        return slice(*args)

def check_slice(option, opt, value):
    """
    returns an int or slice
    """
    try:
        return str2slice_or_int(value)
    except ValueError:
        message = "option %s: invalid slice value: %r" % (opt, value)
        raise OptionValueError(message)

class Option(_Option):
    ATTRS = _Option.ATTRS + ["unspecified"]
    ACTIONS = _Option.ACTIONS + ("load", "update", "update_const",
                                 "update_true", "update_false")
    STORE_ACTIONS = _Option.STORE_ACTIONS + ("load", "update", "update_const",
                                             "update_true", "update_false",
                                             "callback")
    TYPED_ACTIONS = _Option.TYPED_ACTIONS + ("load", "update")
    ALWAYS_TYPED_ACTIONS = _Option.ALWAYS_TYPED_ACTIONS + ("load", "update")
    NARGS_SPECIFIED_ACTIONS = defaultdict(_constant(None), update=2)
    CONST_ACTIONS = set(["store_const", "update_const"])

    # handle type conversion in take_action() not in process()
    TYPE_HANDLING_ACTIONS = set(["load", "update"])

    TYPES = _Option.TYPES + ("slice",)
    TYPE_CHECKER = _Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["slice"] = check_slice

    def _check_const(self):
        if self.action not in self.CONST_ACTIONS and self.const is not None:
            msg = "'const' must not be supplied for action %r" % self.action
            raise OptionError(msg, self)

    def _check_nargs(self):
        nargs_limit = self.NARGS_SPECIFIED_ACTIONS[self.action]
        if nargs_limit is None:
            _Option._check_nargs(self)
        elif self.nargs is None:
            self.nargs = nargs_limit
        elif self.nargs != nargs_limit:
            msg = "'nargs' must be %d for action %r" % (nargs_limit,
                                                        self.action)
            raise OptionError(msg, self)

    CHECK_METHODS = [_Option._check_action,
                     _Option._check_type,
                     _Option._check_choice,
                     _Option._check_dest,
                     _check_const,
                     _check_nargs,
                     _Option._check_callback]

    # defer type conversion
    def process(self, opt, value, values, parser):
        if self.action in self.TYPE_HANDLING_ACTIONS:
            return self.take_action(self.action, self.dest, opt,value, values,
                                    parser)
        else:
            return _Option.process(self, opt, value, values, parser)

    def _update(self, dest, key, dict_value, values):
        values.ensure_value(dest, {})[key] = dict_value

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "load":
            infile = open(value)
            add_values = (self.convert_value(opt, line.rstrip())
                          for line in infile)
            values.ensure_value(dest, []).extend(add_values)
        elif action == "update":
            key = value[0]
            dict_value = self.convert_value(opt, [value[1]])[0]
            self._update(dest, key, dict_value, values)
        elif action == "update_const":
            self._update(dest, key, self.const, values)
        elif action == "update_true":
            self._update(dest, key, True, values)
        elif action == "update_false":
            self._update(dest, key, False, values)
        else:
            _Option.take_action(self, action, dest, opt, value, values, parser)

# XXX: add list of defaults in help
class OptionParser(_OptionParser):
    def __init__(self, usage=None, option_list=None,
                 option_class=Option, *args, **kwargs):
        _OptionParser.__init__(self, usage, option_list, option_class, *args,
                               **kwargs)

class OptionGroup(_OptionGroup):
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.parser.add_option_group(self)

def main(args):
    pass

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
