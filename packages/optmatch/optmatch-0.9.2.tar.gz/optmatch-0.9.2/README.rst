**optmatch** - Library to allow an easy and effective parsing of command line options.

Full documentation: http://coderazzi.net/python/optmatch

**optmatch** is based on expressing the actions -with all options and related flags-
that are supported, instead of just listing all possible argument flags.

For example:

    class Example(**OptionMatcher**):

        **@optset**

        def handle_common_flag(self, **mail_option**):

            ...


        **@optmatcher**

        def handle_compression(self, filename, **compress_flag** =False):

            ...


        **@optmatcher(flags='verbose', options='mode')**

        def handle(self, filename, verbose=False, mode='simple', where=None):

            ...


In this example:


1. It is defined a common flag (--mail)

2. It is defined an action, supporting a --compress flag which is False by default,  and requiring a filename parameter

3. It is defined a second action, supporting a --verbose flag and a --mode option, requiring one or two file locations.



