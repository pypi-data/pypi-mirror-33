"""optmatch - matching command line argument by method's signatures
Support usual GNU/Unix conventions, but not exclusively

Author:  Luis M. Pena <dr.lu@coderazzi.net>
Site:    www.coderazzi.net/python/optmatch
"""

import os.path
import re
import sys
from sre_constants import error as RegularExpresionError

__version__ = '0.9.2'

__all__ = ['optset', 'optmatcher',
           'OptionMatcher', 'OptionMatcherException', 'UsageException']

__copyright__ = """
Copyright (c) Luis M. Pena <lu@coderazzi.net>  All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

_COMMA_SPLIT = re.compile('\\s*,\\s*')

if sys.version_info.major == 2:
    def get_default_values(f):
        return f.func_defaults

    def get_method_name(f):
        return f.im_self.__class__.__name__

    def get_flags_and_parameter_names(f):
        flags, first_arg = f.func_code.co_flags, hasattr(f, 'im_self')
        par_names = f.func_code.co_varnames[first_arg:f.func_code.co_argcount]
        return flags, par_names
else:
    def get_default_values(f):
        return f.__defaults__

    def get_method_name(f):
        return f.__self__.__class__.__name__

    def get_flags_and_parameter_names(f):
        flags, first_arg = f.__code__.co_flags, hasattr(f, '__self__')
        par_names = f.__code__.co_varnames[first_arg:f.__code__.co_argcount]
        return flags, par_names


class Decoration(object):
    """
    Internal namespace to define any decoration functionality
    optmatcher decorator adds an attribute 'optmatcher' that contains
        the list of parameters provided in the decorator definition,
        like flags, options, etc, in a given order
    optset decorator behaves as the optmatcher one, but adds a
        second attribute to the function/method: 'optset', with
        value True
    """

    @staticmethod
    def decorate(optset, *args):
        # Decoration method for optmatcher and optset decorators.
        # Param optset should be True for optset decorators
        # Param args is the ordered parameters allowed in those decorators

        def decorate(f, value):
            try:
                f.optmatcher
                raise OptionMatcherException('Cannot decorate twice the ' +
                                             'method ' + f.__name__)
            except AttributeError:
                pass
            f.optmatcher = value
            if optset:
                f.optset = True
            return f

        # perhaps the base decorator is called with the function to decorate
        # http://coderazzi.net/tnotes/python/decorators_without_arguments.html
        if (args[0] and not any(filter(None, args[1:])) and
                type(args[0]) == type(decorate)):
            return decorate(args[0], [])

        return lambda x: decorate(x, args)

    @staticmethod
    def parse_decoration(func):
        # Parses the optmatcher decoration in the given function.
        # If specified, it returns a tuple Info, group, priority,
        #  or (None, None, None) otherwise, where Info is the ordered list
        #  of the decorator parameters

        def parser(flags=None, options=None, int_options=None,
                   float_options=None, prefixes=None,  priority=None,
                   group=None):
            return ((flags, options, int_options, float_options, prefixes),
                    group, priority)

        try:
            return parser(*func.optmatcher)
        except AttributeError:
            return None, None, None

    @staticmethod
    def get_decorated_methods(instance, defined_as_common):
        # Returns the methods decorated with optmatcher or optset -depending
        # on defined_as_common, priority sorted
        functions_and_priorities = []
        for att in dir(instance):
            f = getattr(instance, att)
            if defined_as_common == hasattr(f, 'optset'):
                info, group, priority = Decoration.parse_decoration(f)
                if info:
                    functions_and_priorities.append((priority or 0, f))
        # sort now by inverse priority, and return just the functions
        functions_and_priorities.sort(key=lambda x: -x[0])
        return [f for (p, f) in functions_and_priorities]


class UsageMode(object):
    """Internal class gathering overall information, like the option prefix"""

    # Available instance attributes:
    #   option      : the option prefix ('--')
    #   assigner    : the string to be used as separator between
    #                 names and values
    #   getopt      : True if getopt mode (short is '-', long options as '--')
    #   options_help : Map containing the help for each known option
    #   var_names    : Map containing the variable name for each known option.
    #                 This is only used for text representation of the options

    def __init__(self, option, assigner):
        self.options_help, self.var_names = None, None
        self.set(option, assigner)

    def set(self, option=None, assigner=None,
            options_help=None, var_names=None):
        """Sets one or more of the mode' variables"""
        self.option = option or self.option
        self.assigner = assigner or self.assigner
        self.options_help = options_help or self.options_help
        self.var_names = var_names or self.var_names
        self.getopt = self.option == '--'

    def get_option_prefix(self, argument):
        """Returns the option prefix for a given argument"""
        if not self.getopt or len(argument) > 1:
            return self.option
        return '-'

    def get_delimiter(self, argument):
        """Returns the assigner string for a given argument"""
        if not self.getopt or len(argument) > 1:
            return self.assigner
        return ' '


class CommandLine(object):
    """Internal class to handle the Command Line arguments
    This class is used by the handlers to iterate through the arguments in
       the command line. The iteration does not need to be argument by
       argument, as one single argument could contain multiple options
       (only in getopt mode,  where -cov could mean -c -o -v)
    """

    # Available instance attributes:
    #   arg    : String, the whole argument, without the prefix option
    #            if the argument were '--option', arg would be 'option'
    #   name   : String, the name of the current argument
    #            if the argument were '--op=2', name would be 'op'
    #   value  : String, the value of the current argument
    #            if the argument were '--op=2', name would be '2'
    #   option : Bool, true if the current argument is an option
    #   is_short: Bool, true if the current arg is a short option

    def __init__(self, args, mode, gnu_mode):
        """param args: the list of arguments to handle (first dismissed)"""
        # re_short is hardcoded to '-' if the option is defined as '--'
        self.re_short = mode.getopt
        self.re_option = mode.option
        self.re_separation = re.compile('(.+?)' + mode.assigner + '(.+)$')
        self.args = args
        self.gnu_mode = gnu_mode
        self.can_be_option = True  # used for gnu_mode
        self.reset()

    def reset(self):
        self.next = 1
        if len(self.args) > 1:
            self._next()

    def get_position(self):
        if self.finished():
            return len(self.args), 0
        in_short = len(self.arg)
        if self.value:
            in_short -= len(self.value)
        return self.next, in_short

    def finished(self):
        return self.next == 1

    def separate(self, what):
        """Separates the passed string into name and value.
        Returns a tuple (status, name, value) where status is True
           if the string was separated
        """
        m = self.re_separation.match(what)
        return m and (True, m.group(1), m.group(2)) or (False, what, None)

    def set_arg_handled(self):
        """Reports that the current argument has been handled.
        It returns True if there are no more arguments to handle or the
            next argument is an option
        """
        if self.next >= len(self.args):
            self.next = 1
        return (self.next == 1) or self._next()

    def set_short_arg_handled(self):
        """Reports that the current (short!) argument has been handled."""
        if self.value:
            self.name, self.value = self.value[0], self.value[1:]
        else:
            self.set_arg_handled()

    def _next(self):
        """Handles the next argument, returning True if it is an option"""
        self.arg = self.args[self.next]
        arg = self.arg  # ...
        self.next += 1
        self.option, self.is_short = False, False
        option = self.arg.startswith(self.re_option)
        if self.can_be_option:
            if option:  # normal (long) option
                arg = self.arg[len(self.re_option):]
                self.option = True
            elif self.re_short and self.arg[0] == '-':
                arg = self.arg[1:]
                self.option, self.is_short, self.split = True, True, False
            else:
                self.can_be_option = not self.gnu_mode
        elif option or (self.re_short and self.arg[0] == '-'):
            raise UsageException('Unexpected argument ' + self.arg +
                                 ' after non option arguments')
        if not arg:
            raise UsageException('Unexpected argument ' + self.arg)
        if self.is_short:
            self.name, self.value = arg[0], arg[1:]
        else:
            self.split, self.name, self.value = self.separate(arg)
        return self.option


class ArgumentInfo(object):
    """Class to represent arguments (options, parameters), for help matters"""

    def __init__(self, name, mode):
        """All arguments have a name, and require knowing the UsageMode"""
        self.name = name
        self.mode = mode
        self.default_provided = False  # needed, as default could be None!
        self.default_value = None

    def __str__(self):
        if self.default_provided:
            format = '[%s%s%s%s]'
            if self.default_value is None:
                default = ''
            else:
                default = ' (' + str(self.default_value) + ')'
        else:
            format = '%s%s%s%s'
            default = ''
        return format % (self._get_prefix(), self.name,
                         self._get_suffix(), default)

    def set_default_value(self, default_value):
        """Sets the default value, even if it is None"""
        self.default_provided = True
        self.default_value = default_value

    def _get_prefix(self, name=None):
        """This is the prefix for the argument (-- for options, i.e.)"""
        return ''

    def _get_suffix(self, name=None):
        """This is the prefix for the argument (=MODE, i.e.)"""
        return ''


class VarArgumentInfo(ArgumentInfo):

    def __init__(self):
        self.default_provided = True

    def __str__(self):
        return '...'


class FlagInfo(ArgumentInfo):
    """Flags are arguments with aliases, and with a prefix (--, i.e.)"""

    def __init__(self, aliases, mode):
        """The name of a flag/option is the largest of its aliases"""
        aliases.sort(key=len)
        ArgumentInfo.__init__(self, aliases[-1], mode)
        self.aliases = aliases

    def aliases_as_str(self):
        """Produces, for example: "-m MODE, --mode MODE" """
        return ', '.join(['%s%s%s' % (self._get_prefix(i), i,
                                      self._get_suffix(i))
                          for i in self.aliases])

    def get_doc(self):
        """Returns the doc provided for the given aliases"""
        # it is enough to give the doc for one of the aliases, no check
        # to verify if different aliases have different documentation
        if self.mode.options_help:
            for a in self.aliases:
                try:
                    return self.mode.options_help[a]
                except KeyError:
                    pass

    def _get_prefix(self, name=None):
        return self.mode.get_option_prefix(name or self.name)


class OptionInfo(FlagInfo):
    """Options are flags that add a suffix: -m MODE, instead of -m, i.e. """

    def _get_suffix(self, name=None):
        # for a set of aliases, like 'm', 'mode', the variable name is,
        # by default, the uppercase of the longuer alias. It can be
        # overriden if the user provided a var name for one of the aliases
        def get_variable_name():
            if self.mode.var_names:
                for alias in self.aliases:
                    try:
                        return self.mode.var_names[alias]
                    except KeyError:
                        pass
            return self.name.upper().replace('-', '_')

        return self.mode.get_delimiter(name or self.name) + get_variable_name()


class PrefixInfo(OptionInfo):
    """Prefixes are flags that add a suffix: -m MODE, instead of -m, i.e. """


class OptMatcherInfo(object):
    """Internal class, holds the information associated to each matcher"""

    _NON_ALPHANUM = re.compile('[^a-zA-Z0-9]')
    DECORATOR_ASSIGN = re.compile('(.+?)\\s+as\\s+(.+)')
    FLAG_PATTERN = re.compile('(.+)'
                              '(Flag|Option|OptionInt|OptionFloat|Prefix|'
                              '_flag|_option|_option_int|'
                              '_option_float|_prefix)$')

    def __init__(self, func, mode):
        self.mode = mode
        self._initialize_parameters_information(func)

        # With getoptmode, in addition to the normal definitions, users
        # can specify short options, stored in sorted_defs
        self.defs = set()  # definitions (flags/options/prefixes)
        if mode.getopt:
            self.short_defs = set()
        else:
            self.short_defs = self.defs

        # populate now self.short_defs and short.defs
        for group in self.flags, self.options, self.prefixes:
            for name in group.keys():
                def_set = self._get_defs_group(name)
                if name in def_set:  # for example, defining kFlag and kOption
                    raise OptionMatcherException('%s: %s' % (self.describe(),
                                                             name))
                def_set.add(name)

    def _get_defs_group(self, name):
        if len(name) == 1:
            # note that, in non getopt mode, short_defs points to defs
            return self.short_defs
        return self.defs

    def _initialize_parameters_information(self, func):
        # Initializes all parameter information associated to the function:
        # Note that the index number associated to the first parameter
        # is 1, not zero. This simplifies later many checks
        self.flags = {}  # maps flag name to parameter index
        self.options = {}  # maps option name to parameter index
        self.prefixes = {}  # maps prefix name to parameter index
        self.converts = {}  # maps from index (option) to convert function
        # self.pars maps parameter index to parameter name - a parameter
        # is any method' variable that is not a flag, option, prefix, etc
        self.pars = {}
        self.last_arg = 1  # the last available variable index plus 1
        self.orphan_flags = 0  # flags without associated variable
        self.func = func

        par_names, self.vararg, kwarg = self._get_parameters_info(func)
        # if kwargs are supported, kwargs is used as a dictionary
        self.kwargs = kwarg and not self.mode.getopt and {}
        # note that self.group is used for 'applies' and 'exclusive'
        decoration, self.group, priority = Decoration.parse_decoration(func)
        if decoration and any(filter(None, decoration)):
            self._initialize_parameters_from_decorator(par_names, *decoration)
        else:
            self._initialize_parameters_from_signature(par_names)

            # get default values
        defs = list(get_default_values(func) or [])
        first_def = self.last_arg - len(defs)
        self.defaults = dict([(i + first_def, d) for i, d in enumerate(defs)])

    def _initialize_parameters_from_signature(self, par_names):
        # Initializes the metadata from the function's parameter names

        def uncamel(word):
            """Converts camel_case or underscores into hyphenation"""
            if '_' in word:  # using underscores, no camel case
                return word.replace('_', '-')
            ret, transform = [], False
            for i in word:
                if transform and i.isupper():
                    ret.append('-')
                    i = i.lower()
                ret.append(i)
                transform = i.islower()
            return ''.join(ret)

        used = set()
        for var in par_names:
            match = self.FLAG_PATTERN.match(var)
            if match:
                use_name, what = uncamel(match.group(1)), match.group(2)
                if what in ['Flag', '_flag']:
                    goes = self.flags
                elif what in ['Prefix', '_prefix']:
                    goes = self.prefixes
                else:
                    goes = self.options
                    if what in ['OptionInt', '_option_int']:
                        self.converts[self.last_arg] = self._as_int
                    elif what in ['OptionFloat', '_option_float']:
                        self.converts[self.last_arg] = self._as_float
                if use_name in used:
                    raise OptionMatcherException(
                        '%s: Invalid parameter reuse: %s' %
                        (self.describe(), use_name))
                used.add(use_name)
                goes[use_name] = self.last_arg
            else:
                self.pars[self.last_arg] = var
            self.last_arg += 1

    def _initialize_parameters_from_decorator(self, par_names, flags, options,
                                              int_options, float_options,
                                              prefixes):

        def get_decoration_definitions(decoration):
            # The returned value maps names to 'as' values, if present, or to
            #  None, otherwise, for a given decoration argument
            ret = {}
            if decoration:
                try:
                    defs = _COMMA_SPLIT.split(decoration.strip())
                except (AttributeError, TypeError):
                    raise OptionMatcherException('Invalid definition')
                for d in defs:
                    if d:
                        match = self.DECORATOR_ASSIGN.match(d)
                        if match:
                            ret[match.group(1)] = match.group(2)
                        else:
                            ret[d] = None
            return ret

        # variables match is done dismissing any non alphanumerical characters
        # this would match an option 'import-folder' to a variable
        # import_folder (but also import__folder).
        # It also enables the usage of reserved words: a flag 'import' could
        # be associated to a variable import_', for example
        par_names = [self._NON_ALPHANUM.sub('', v) for v in par_names]
        ints, floats, used = {}, {}, set()
        for att, group in [(self.flags, flags),
                           (self.options, options),
                           (self.prefixes, prefixes),
                           (ints, int_options),
                           (floats, float_options)]:
            # in the following loop, n defines each parameter name given
            # in the decorator for each group (flags, options, etc), while
            # v defines the public name (n as v)
            for name, value in get_decoration_definitions(group).items():
                # get the index of the var: is an error if not found or
                # if it is reused
                try:
                    index = par_names.index(self._NON_ALPHANUM.sub('', name))
                except ValueError:
                    if att is self.flags and not value:
                        # a flag could be not existing as argument, as
                        # the flag value is not really interesting. In this
                        # case, makes no sense defining it as 'var as name'
                        self.orphan_flags -= 1
                        att[name] = self.orphan_flags
                        continue
                    raise OptionMatcherException('%s: Invalid argument: %s' %
                                                 (self.describe(), name))
                par = value or name
                if par in used:
                    raise OptionMatcherException(
                        '%s: Invalid parameter reuse: %s' %
                        (self.describe(), name))
                used.add(par)
                att[par] = 1 + index

        # all groups are created as maps (name -> variable index), but for
        # params we invert the map, as the index is the important information
        self.pars = dict([(i + 1, v) for i, v in enumerate(par_names)
                          if i not in used])
        # int_options and float_options are options with additional checks:
        self.options.update(ints)
        self.options.update(floats)
        self.converts = dict([(i, self._as_float) for i in floats.values()])
        self.converts.update(dict([(i, self._as_int) for i in ints.values()]))
        self.last_arg = len(par_names) + 1

    def applies_to_matcher(self, matcher_handler):
        """Returns true if this 'optset' handler applies to the matcher"""
        if not self.group:  # the user didn't specify an 'applies'
            # in this case, it applies if the matcher is not exclusive
            return not matcher_handler.group
        # only invoked on optset' methods, where self.gorup is None or a r.e.
        return self.group.match(matcher_handler.func.__name__) is not None

    def support_vargs(self):
        """Returns whether it accepts *vars"""
        return self.vararg > 0

    def supports_k_w_args(self):
        """Returns whether it accepts **kargs argument"""
        return isinstance(self.kwargs, dict)

    def get_options(self):
        """Returns the defined flags, options and prefixes
        as a list of ArgumentInfo instances (FlagInfo or OptionsInfo, in fact)
        """

        def get_options_and_defaults(group, constructor):
            ret, options = [], {}
            # flags, options and prefixes are map name -> index
            # but with the aliases, multiple names can point to the same index
            for name, index in group.items():
                options.setdefault(index, []).append(name)
            for index, aliases in options.items():
                this = constructor(aliases, self.mode)
                try:
                    this.set_default_value(self.defaults[index])
                except KeyError:
                    pass
                ret.append(this)
            ret.sort(key=lambda x: x.name)
            return ret

        return (get_options_and_defaults(self.flags, FlagInfo)
                + get_options_and_defaults(self.options, OptionInfo)
                + get_options_and_defaults(self.prefixes, PrefixInfo))

    def get_parameters(self):
        """Returns the defined parameters as a [ArgumentInfo instances]"""
        ret = []
        for i in range(1, self.last_arg):
            try:
                info = ArgumentInfo(self.pars[i], self.mode)
            except KeyError:
                continue
            try:
                info.set_default_value(self.defaults[i])
            except KeyError:
                pass
            ret.append(info)
        return ret

    def set_aliases(self, aliases):
        """Sets aliases between option definitions."""

        # Aliases affect to all possible options (flags/options/prefixes).
        # If there is a flag 'v' at index 2, and an alias is defined for 'v'
        #  as 'verbose', flags will be extended with 'verbose' : 2
        # In addition, defs (and/or shortdefs) is extended with the new alias
        def set_alias(a, b, aSet, bSet):
            # Defines b as an alias in bSet of a, if a is defined in aSet
            # As a result, any option defined as 'a' will be used if the
            #      user specifies the 'b'
            ret = a in aSet
            if ret:
                if b in bSet:
                    raise OptionMatcherException(
                        'Bad alias:' + a + '/' + b + ' in ' + self.describe())
                bSet.add(b)
                for each in self.flags, self.options, self.prefixes:
                    try:
                        each[b] = each[a]
                    except KeyError:
                        pass
            return ret

        for s, t in aliases.items():
            if self.mode.getopt:
                # In getoptmode, aliases must map short and long options,
                #   that is, options with 1 character and options with more
                #   than 1 character
                if len(s) > len(t):
                    s, t = t, s
                if len(s) > 1 or len(t) == 1:
                    raise OptionMatcherException('Bad alias:' + s + '/' + t)
                if set_alias(t, s, self.defs, self.short_defs):
                    continue
            elif t in self.defs:
                # if alias 'l' is already known, we try setting from s->l
                s, t = t, s
            set_alias(s, t, self.short_defs, self.defs)

    def get_index_name(self, index):
        # returns the flag/option/parameter name with the given index
        # (no prefixes) Note that it will be returned any of its aliases
        for n, v in self.flags.items():
            if v == index:
                return 'flag ' + n
        for n, v in self.options.items():
            if v == index:
                return 'option ' + n
        return 'parameter ' + self.pars[index]

    def describe(self):
        """Describes the underlying method"""
        try:
            name = 'method ' + get_method_name(self.func) + '.'
        except AttributeError:
            name = 'function '
        return name + self.func.__name__

    def get_doc(self):
        """Return the documentation of the underlying method, if any"""
        return self.func.__doc__

    def _get_parameters_info(self, f):
        # This information includes: the list of variables, if it supports
        #   varargs, and if it supports kwargs
        flags, var_names = get_flags_and_parameter_names(f)
        return list(var_names), (flags & 0x0004) != 0, (flags & 0x0008) != 0

    def _as_int(self, value):
        return int(value)

    def _as_float(self, value):
        return float(value)


class OptMatcherHandler(OptMatcherInfo):
    """Internal class, representing each specific matcher handler.
    It is an OptMatcherInfo extended with operations to handle arguments
    """

    def __init__(self, func, mode):
        OptMatcherInfo.__init__(self, func, mode)
        self.reset()

    def reset(self):
        # all prefixes are reset as provided as an empty list
        self.provided = dict([(i, []) for i in self.prefixes.values()])
        self.provided_pars = []

    def invoke(self):
        """Invokes the underlying function, unless it cannot be invoked."""
        # It is invoked using the options/parameters/defaults already setup
        status, args, kwargs = self._get_invoking_pars()
        return (status is None) and self.func(*args, **kwargs)

    def check_invokable(self, required):
        """Verifies whether the underlying function can be invoked."""

        def something_provided():
            # just check if the user provided any value.
            return self.provided_pars or any(filter(lambda x: x != [],
                                                    self.provided.values()))

        # It can, if all the options/parameters are specified or have defaults
        error_reason = self._get_invoking_pars()[0]
        return (required or something_provided()) and error_reason

    def _get_invoking_pars(self):
        # Returns the parameters required to invoke the underlying function.
        # It returns a tuple (problem, *args, **kwargs)
        args, parameters = [], self.provided_pars[:]
        # we only check the indexes 1...last_arg, so the orphan flags are not
        # checked here (they are not used to invoke the method)
        for i in range(1, self.last_arg):
            try:
                value = self.provided[i]  # read first the provided value
            except KeyError:
                # otherwise, the current index could refer to a parameter,
                # which are stored separately
                if i in self.pars and parameters:
                    value = parameters.pop(0)
                else:
                    # this argument were not provided: try the default value
                    try:
                        value = self.defaults[i]
                    except KeyError:
                        # Neither, this function cannot be invoked
                        return ('Missing required ' + self.get_index_name(i),
                                None, None)
            args.append(value)
        # if the function defined a *arg parameter, it can handle the
        # remaining provided parameters (if not, we would had already an error)
        args.extend(parameters)
        # It must be still checked the orphan flags' variables
        # These are not passed to the method, but must have been provided to
        # consider that the method can be invoked
        for c in range(self.orphan_flags, 0):
            if c not in self.provided:
                return 'Missing required ' + self.get_index_name(c), None, None

        return None, args, self.kwargs or {}

    def handle_arg(self, command_line):
        """Handles one argument in the command line"""
        # Returns None if ok, otherwise the reason why it cannot consume the
        #  argument
        # An exception is raised in not recoverable situations: like flag not
        #     provided when needed, etc
        # This handling can imply, under getopt mode, consuming more
        # than one argument in the command line, or just a portion
        # of one, if a short option was specified

        # Check first options (short/long)
        if command_line.option:
            if command_line.is_short:
                return self._handle_short_arg(command_line)
            return self._handle_long_arg(command_line)
        # If not, it is a parameter, but perhaps there are already too many...
        if not self.vararg and (len(self.provided_pars) >= len(self.pars)):
            return 'Unexpected argument: ' + command_line.arg

        self.provided_pars.append(command_line.arg)
        command_line.set_arg_handled()
        return None

    def _handle_long_arg(self, cmd):
        """Handles one long argument in the command line."""
        name = cmd.name
        # only check the name if defined (and not defined as a short option)
        ok_name = name in self.defs
        if ok_name and self._handle_option(cmd):
            return None

        flag = ok_name and self.flags.get(name, None)
        if flag:
            if cmd.split:  # flag, but user specified a value
                raise UsageException('Incorrect flag ' + name)
            self.provided[flag] = True
        else:
            prefix, name = self._split_prefix(name)
            if prefix:
                if not name:
                    # perhaps is given as -D=value(bad) or separate (getopt)
                    if (cmd.split or not self.mode.getopt or
                            cmd.set_arg_handled()):
                        raise UsageException(
                            'Incorrect prefix usage on argument ' + cmd.arg)
                    # note that cmd.value is the value of next argument now
                    name = cmd.name
                self.provided[prefix].append((name, cmd.value))
            else:  # try now the self.kwargs, if possible
                try:
                    self.kwargs[cmd.name] = cmd.value
                except TypeError:
                    # no kwargs, this argument cannot be used
                    return 'Unexpected argument: ' + cmd.arg
        cmd.set_arg_handled()

    def _handle_short_arg(self, cmd):
        """Handles one short argument in the command line"""
        # This method is only called for getopt mode
        name = cmd.name
        if name not in self.short_defs:
            # in shorts, name is just one letter, so not inclusion in
            # short_defs means that it is neither a prefix, do no more checks
            return 'Unexpected flag ' + name + ' in argument ' + cmd.arg
        flag = self.flags.get(name, None)
        if flag:
            self.provided[flag] = True
            cmd.set_short_arg_handled()
        elif not self._handle_option(cmd):
            prefix = self.prefixes.get(name, None)
            # no flag, no option, but in short_defs->is a prefix!
            if not cmd.value:
                # given separately
                if cmd.set_arg_handled():
                    raise UsageException('Incorrect prefix ' + name)
                cmd.value = cmd.arg
            self.provided[prefix].append(cmd.separate(cmd.value)[1:])
            cmd.set_arg_handled()
        return None

    def _handle_option(self, cmd):
        """Checks if the command is a valid option, handling it if so
           Returns the option handled, or None if not handled
        """
        # the normal case, -name=value, implies command.value
        name = cmd.name
        option = self.options.get(name, None)
        if option:
            if cmd.value:
                value = cmd.value
            else:
                # under getoptmode, this is still valid if the value is
                # provided as a separate argument (no option, no split)
                if not self.mode.getopt or cmd.set_arg_handled() or cmd.split:
                    raise UsageException('Incorrect option ' + name)
                value = cmd.arg
            # If a conversion is needed (to integer/float), do it now
            try:
                value = self.converts[option](value)
            except KeyError:
                # no conversion required, we treat it always as file
                value = os.path.expanduser(os.path.expandvars(value))
            except ValueError:
                raise UsageException('Incorrect value for ' + name)
            self.provided[option] = value
            cmd.set_arg_handled()
        return option

    def _split_prefix(self, name):
        # Splits an existing prefix from the given name.
        #   It does not apply to short prefixes (getopt mode)
        #   It returns the tuple (prefix, rest), or (None, None) if not found
        for each in self.prefixes:
            if each in self.defs and name.startswith(each):
                return self.prefixes[each], name[len(each):]
        return None, None


class UsageAccessor(object):
    """Class to access and to format usage info"""

    def __init__(self, handlers, mode):
        self.mode = mode
        self.handlers = handlers  # each is a list [matcher, optsets...]
        self.reset()

    def get_content(self):
        """Format method, returns the current content"""
        return '\n'.join(self.content)

    def reset(self, width=72):
        """Format method, clears the content"""
        self.content = ['']
        self.width = width

    def add_line(self, content=None, column=0):
        """
        Format method, adds a new line, and places the content on the
        given column. See add method
        """
        self.content.append('')
        if content:
            self.add(content, column)

    def add(self, content, column=0):
        """
        Format method, adds content on the current line at the given position.
        If the current content already covers that column, a new one is
        inserted.
        If the content spawns multiple lines, each start at the
        same position
        The content can be a string, or a list of objects. As a list
        of objects, splitting on multiple lines can only happen for full
        objects; for strings, it is done at each space character.
        No care is taken for any special characters, specially '\n'
        """
        if isinstance(content, str):
            content = content.split(' ')
        current = self.content.pop()
        if (column > 0) and current and (len(current) + 1 > column):
            self.content.append(current)
            current = ''
        started = not column and len(current.strip()) > 0
        current += ' ' * (column - len(current))
        for each in content:
            each = str(each)
            if started and (len(current) + len(each) >= self.width):
                self.content.append(current)
                current = ' ' * column
                started = False
            if each or started:
                if started:
                    current += ' '
                current += each
                started = True
        self.content.append(current.rstrip())

    def get_usage_string(self, width=72, column=24, ident=2,
                         include_usage=True, include_alternatives=True):
        """Generic method to print the usage. By default, the window
        output is limited to 72 characters, with information for each option
        positioned on the column 24.
        """
        self.reset(width)
        if not self.handlers:
            self.add('Error, no usage configured')
        else:
            options = self.get_all_options()
            alternatives = self.get_alternatives()
            alt_options = [self.get_options(a) for a in range(alternatives)]
            alt_params = [self.get_parameters(a) for a in range(alternatives)]
            if include_usage:
                self.add('Usage:')
                if alternatives == 1:
                    # if there is one single alternative, it is shown fully
                    # expanded, with options and default values
                    self.add(alt_options[0] + alt_params[0])
                else:
                    # Otherwise, get_all_parameters provide the intersection of
                    # names among all alternatives
                    if options:
                        self.add('[common options]')
                    self.add(self.get_all_parameters())
                self.add_line()
            if options:
                # aliases and doc for each option is shown next
                self.add_line('options:')
                for each in options:
                    self.add_line(each.aliases_as_str(), ident)
                    doc = each.get_doc()
                    if doc:
                        self.add(doc, column)
            if include_alternatives and alternatives > 1:
                # finally, all the alternatives, fully expanded
                self.add_line()
                self.add_line('alternatives:')
                for i in range(alternatives):
                    content = alt_options[i] + alt_params[i]
                    self.add_line()
                    self.add_line('*')
                    self.add(content, ident)
                    doc = self.get_doc(i)
                    if doc:
                        self.add_line()
                        for line in doc.split('\n'):
                            if line.strip():
                                self.add(line, column)
        return self.get_content()

    def get_alternatives(self):
        """Returns the number of provided matchers"""
        return len(self.handlers)

    def get_doc(self, alternative):
        """Returns the documentation for the given matcher"""
        return self.handlers[alternative][0].get_doc()

    def get_parameters(self, alternative):
        """Returns the parameters (as ArgumentInfo) for the given matcher"""
        ret = []
        for h in self.handlers[alternative]:  # matcher goes always first
            ret.extend(h.get_parameters())
            if h.support_vargs():
                # We break here, if a matcher defines parameters,
                # they will be never handled, as the common matcher would
                # consume them first
                ret.append(VarArgumentInfo())
                break
        # if a parameter is mandatory, previous ones cannot be optional
        set = False
        for i in range(len(ret) - 1, -1, -1):
            if not set:
                set = not ret[i].default_provided
            else:
                ret[i].default_provided = False
        return ret

    def get_all_parameters(self):
        """Returns all the expected parameters (as strings)
        The list will include the number of parameter of the matcher with
         more mandatory parameters (plus the parameters in the common one)
        """
        ret, all_pars, varargs = [], [], False
        for c, handlers in enumerate(self.handlers):
            pars = []
            for h in handlers:
                pars.extend(h.get_parameters())
                if h.support_vargs():
                    varargs = True
                    break
            all_pars.append(pars)
        #  all_pars contain lists of the list of params for each handler
        #  doing now for c, each in enumerate(map(None, *all_pars)):
        max_len = max([len(each) for each in all_pars])
        all_pars_homogenized = zip(*[each + [None] * (max_len - len(each))
                                     for each in all_pars])
        for c, each in enumerate(all_pars_homogenized):
            name = None
            for i in each:
                if i:
                    if not name:
                        name = i.name
                    elif name != i.name:
                        name = 'arg%d' % (c + 1)
                        break
            ret.append(name)
        if varargs:
            ret.append(str(VarArgumentInfo()))
        return ' '.join(ret)

    def get_all_options(self):
        """Returns -as FlagInfo instances-, all the flags/options/prefixes
        that were defined for any of the provided matchers. The list
        will be sorted alphabetically, listing first the flags
        """
        # Search is done over all the matchers, with priority on the common
        options = {}
        for i in range(self.get_alternatives()):
            self._build_options(i, options)
        ret = list(options.values())
        ret.sort(key=lambda x: (isinstance(x, OptionInfo), x.name.lower()))
        return ret

    def get_options(self, alternative):
        """Returns -as FlagInfo instances-, all the flags/options/prefixes
        that were defined for the given matcher, including
        those associated to the common matcher. The list
        will be sorted alphabetically, listing last the optional options
        """
        ret = list(self._build_options(alternative, {}).values())
        ret.sort(key=lambda x: (x.default_provided, x.name.lower()))
        return ret

    def _build_options(self, alternative, options):
        # Adds all the options of the given alternative to the passed options
        for h in self.handlers[alternative]:
            for option in h.get_options():
                if option.name not in options:
                    options[option.name] = option
            if h.supports_k_w_args():
                break
        return options


class OptionMatcher(object):
    """ Class handling command line arguments by matching method parameters.
    It supports naturally the handling of mutually exclusive options.
    """

    def __init__(self, aliases=None, options_help=None,
                 option_var_names=None, option_prefix='--', assigner='=',
                 default_help=True):
        """
        Param aliases is a map, allowing setting option aliases.
            In getopt mode, all aliases must be defined between a short
            (1 character length) option and a long (>1 character length)
            option
        Param options_var_names identifies, for options and prefixes, the
            variable name used during the usage output. For example,
            option 'm' would be visualized by default as '-m M', unless
            this option is used.
            For aliases, it is possible to define the var name for
            any of the given aliases -if different names are supplied
            for two aliases of the same option, one will be dismissed-
        Param options_help defines the information associated to each
            option. It is map from option's name to its documentation.
            For aliases, it is possible to define the documentation for
            any of the given aliases -if different info is supplied
            for two aliases of the same option, one will be dismissed-
        Param options_var_names identifies, for options and prefixes, the
            variable name used during the usage output. For example,
            option 'm' would be visualized by default as '-m M', unless
            this option is used.
            For aliases, it is possible to define the var name for
            any of the given aliases -if different names are supplied
            for two aliases of the same option, one will be dismissed-
        Param option_prefix defines the prefix used to characterize an argument
            as an option. If is defined as '--', it implies
            automatically getopt mode, which enables the usage of short
            options with prefix -
        Param assigner defines the character separating options' name
            and value
        Param default_help is True to automatically show the usage when the
            user requests the --help option (or -h)
        """
        self._mode = UsageMode(option_prefix, assigner)
        self.enable_default_help(default_help)
        self.set_aliases(aliases)
        self.set_usage_info(options_help, option_var_names)

    def enable_default_help(self, set=True):
        """Enables the default help, under 'h' or 'help' """
        self._default_help = set
        return self

    def set_aliases(self, aliases):
        """Sets the aliases. See __init__"""
        self._aliases = aliases
        return self

    def set_usage_info(self, options_help, option_var_names):
        """Sets the usage information for each option. See __init__"""
        self._mode.set(options_help=options_help, var_names=option_var_names)
        return self

    def set_mode(self, option_prefix, assigner):
        """Sets the working mode. See __init__"""
        self._mode.set(option=option_prefix, assigner=assigner)
        return self

    def get_usage(self):
        """Returns an Usage object to handle the usage info"""
        matcher_handlers, common_handlers = self._create_handlers()
        handlers = [[m] + list(filter(lambda x: x.applies_to_matcher(m),
                                      common_handlers))
                    for m in matcher_handlers]
        return UsageAccessor(handlers, self._mode)

    def print_help(self):
        """shows the help message"""
        print(self.get_usage().get_usage_string())

    def process(self, args, gnu=False, handle_usage_problems=True):
        """Processes the given command line arguments
        Param gnu determines gnu behaviour. Is True, no-option
            arguments can be only specified latest
        Param handle_usage_problems. If not False, it automatically catches
            UsageExceptions, returning the value handle_usage_problems
        """
        matchers, commons = self._create_handlers()
        command_line = CommandLine(args, self._mode, gnu)
        highest_problem = (-1, 0), 'Invalid command line input'

        # the method is simple: for each matcher, we verify if the arguments
        # suit it, taking in consideration the common handler, if given.
        # As soon as a matcher can handle the arguments, we invoke it, as well
        # as the common handler, if given.
        try:
            for handler in matchers:
                # only use the common handlers that apply to the matcher
                assoc_commons = list(filter(lambda x:
                                            x.applies_to_matcher(handler),
                                            commons))
                problem = self._try_handlers(assoc_commons,
                                             handler, command_line)
                if not problem:
                    # ok: invoke common handler, then matcher's handler
                    for each in assoc_commons:
                        each.invoke()
                    return handler.invoke()
                position = command_line.get_position()
                if position > highest_problem[0]:
                    highest_problem = position, problem
                    # prepare command line, common handlers for next loop
                command_line.reset()
                for each in commons:
                    each.reset()
            raise UsageException(highest_problem[1])
        except UsageException as ex:
            if handle_usage_problems is not False:
                import sys
                sys.stderr.write(str(ex) + '\n')
                return handle_usage_problems
            else:
                raise

    def _create_handlers(self):
        # Returns all the required handlers, as a tuple
        # the first element is the list of matchers, and the second, the
        # common matcher
        def create_handle(function):
            if not function:
                return None
            ret = OptMatcherHandler(function, self._mode)
            if self._aliases:
                ret.set_aliases(self._aliases)
            return ret

        if self._default_help:
            if self._mode.getopt:
                self._aliases = self._aliases or {}
                self._aliases['h'] = 'help'
            self._mode.options_help = self._mode.options_help or {}
            self._mode.options_help['help'] = 'shows this help message'

        matchers = [create_handle(f)
                    for f in Decoration.get_decorated_methods(self, False)]

        if not matchers:
            raise OptionMatcherException("No matchers defined")

        commons = [create_handle(f)
                   for f in Decoration.get_decorated_methods(self, True)]

        if self._default_help:
            # cannot decorate directly print_help, any instance would
            # get the decoration!
            def surrogate(): return self.print_help()
            surrogate.__doc__ = self.print_help.__doc__
            matchers.append(create_handle(optmatcher(
                flags='help', exclusive=True)(surrogate)))

        return matchers, commons

    def _try_handlers(self, common_handlers, command_handler, command_line):
        # Checks if the specified handlers can process the command line.
        # If so, it returns None, letting the handlers ready to be invoked
        # Otherwise, it returns the reason why it cannot be handled
        handlers = [command_handler] + common_handlers
        while not command_line.finished():
            for each in handlers:
                problem = each.handle_arg(command_line)
                if not problem:
                    break
            else:
                if problem:
                    return problem
        for each in common_handlers:
            problem = each.check_invokable(False)
            if problem:
                return problem
        return command_handler.check_invokable(True)


class OptionMatcherException(Exception):
    """Exception raised when a problem happens during handling setup"""


class UsageException(OptionMatcherException):
    """Exception raised while handling an argument"""


def optmatcher(flags=None, options=None, int_options=None, float_options=None,
               prefixes=None, priority=None, exclusive=False):
    """Decorator defining a function / method as optmatcher choice"""

    if exclusive not in [True, False]:
        raise OptionMatcherException('exclusive value must be True or False')

    return Decoration.decorate(False, flags, options, int_options,
                               float_options, prefixes, priority,
                               exclusive)


def optset(flags=None, options=None, int_options=None, float_options=None,
           prefixes=None, priority=None, applies=None):
    """Decorator defining a function / method as optset choice"""

    if applies is not None:
        try:
            # convert applies into a regular expression, if possible
            # i.e, handle, handle_b* is converted into (handle|handle_b.*)
            converted = [each.replace('*', '.*')
                         for each in _COMMA_SPLIT.split(applies.strip())]
            applies = re.compile('^(' + '|'.join(converted) + ')$')
        except RegularExpresionError:
            raise OptionMatcherException('Invalid applies value: ' + applies)

    return Decoration.decorate(True, flags, options, int_options,
                               float_options, prefixes, priority, applies)
