from six.moves import cStringIO as StringIO
import ast
import sys
import itertools as it
import tokenize
import re


_INDENT_RE = re.compile('^([ ]*)(?=\S)', re.MULTILINE)


_EXCEPTION_RE = re.compile(r"""
    # Grab the traceback header.  Different versions of Python have
    # said different things on the first traceback line.
    ^(?P<hdr> Traceback\ \(
        (?: most\ recent\ call\ last
        |   innermost\ last
        ) \) :
    )
    \s* $                # toss trailing whitespace on the header.
    (?P<stack> .*?)      # don't blink: absorb stuff until...
    ^ (?P<msg> \w+ .*)   #     a line *starts* with alphanum.
    """, re.VERBOSE | re.MULTILINE | re.DOTALL)


class DoctestPart(object):
    def __init__(self, source, want, line_offset):
        self.source = source
        self.want = want
        self.line_offset = line_offset

    def check_got_vs_want(self, got):
        if not self.want:
            return True
        if self.want:
            if self.want == '...':
                return True
            if got.endswith('\n') and not self.want.endswith('\n'):
                # allow got to have one extra newline
                got = got[:-1]
            if self.want == got:
                return True

        raise AssertionError(
            'got={!r} differs with doctest want={!r}'.format(got, self.want))


class DoctestParser(object):

    def __init__(self, simulate_repl=False):
        self.simulate_repl = simulate_repl

    def parse(self, string):
        """
        Divide the given string into examples and intervening text.

        Example:
            >>> s = 'I am a dummy example with two parts'
            >>> x = 10
            >>> print(s)
            I am a dummy example with three parts
            >>> s = 'My purpose it so demonstrate how wants work here'
            >>> print('The new want applies ONLY to stdout')
            >>> print('given before the last want')
            >>> '''
                this wont hurt the test at all
                even though its multiline '''
            >>> y = 20
            The new want applies ONLY to stdout
            given before the last want
            >>> # Parts from previous examples are executed in the same context
            >>> print(x + y)
            30

            this is simply text, and doesnt apply to the previous doctest the
            <BLANKLINE> directive is still in effect.

        Example:
            >>> from xdoctest import doctest_parser
            >>> from xdoctest import docscrape_google
            >>> from xdoctest import core
            >>> self = doctest_parser.DoctestParser()
            >>> docstr = self.parse.__doc__
            >>> blocks = docscrape_google.split_google_docblocks(docstr)
            >>> doclineno = self.parse.__func__.__code__.co_firstlineno
            >>> key, (string, offset) = blocks[-2]
            >>> self._label_docsrc_lines(string)
            >>> doctest_parts = self.parse(string)
            >>> assert len(doctest_parts) == 4
        """
        string = string.expandtabs()
        # If all lines begin with the same indentation, then strip it.
        min_indent = min_indentation(string)
        if min_indent > 0:
            string = '\n'.join([l[min_indent:] for l in string.split('\n')])

        labeled_lines = self._label_docsrc_lines(string)

        grouped_lines = self._group_labeled_lines(labeled_lines)

        output = list(self._package_groups(grouped_lines))
        return output

    def _package_groups(self, grouped_lines):
        lineno = 0
        for chunk in grouped_lines:
            if isinstance(chunk, tuple):
                source_lines, want_lines = chunk
                for example in self._package_chunk(source_lines, want_lines,
                                                   lineno):
                    yield example
                lineno += len(source_lines) + len(want_lines)
            else:
                text_part = '\n'.join(chunk)
                yield text_part
                lineno += len(chunk)

    def _package_chunk(self, source_lines, want_lines, lineno=0):
        """
        if `self.simulate_repl` is True, then each statment is broken into its
        own part.  Otherwise, statements are grouped by the closest `want`
        statement.
        """
        match = _INDENT_RE.search(source_lines[0])
        line_indent = 0 if match is None else (match.end() - match.start())
        # indent = min_indent + line_indent
        norm_source_lines = [p[line_indent + 4:] for p in source_lines]

        s1 = 0
        if self.simulate_repl:
            # for compatibility we break down each source block into individual
            # statements. (We need to remember to move PS2 lines in with the
            # previous PS1 line)
            ps1_linenos = self._locate_ps1_linenos(source_lines, line_indent)

            # Break down first parts which dont have any want
            for s1, s2 in zip(ps1_linenos, ps1_linenos[1:]):
                self._locate_ps1_linenos(source_lines, line_indent)
                source = '\n'.join(norm_source_lines[s1:s2])
                # options = self._find_options(source, name, lineno + s1)
                # example = DoctestPart(source, None, None, lineno=lineno + s1,
                #                       indent=indent, options=options)
                example = DoctestPart(source, want=None, line_offset=lineno + s1)
                yield example
        else:
            ps1_linenos = [0]

        # the last part has a want
        last = ps1_linenos[-1]
        source = '\n'.join(norm_source_lines[last:])
        # If `want` contains a traceback message, then extract it.
        norm_want_lines = [p[line_indent:] for p in want_lines]
        want = '\n'.join(norm_want_lines)

        # m = _EXCEPTION_RE.match(want)
        # exc_msg = m.group('msg') if m else None

        example = DoctestPart(source, want=want, line_offset=lineno + s1)
        yield example

    def _group_labeled_lines(self, labeled_lines):
        # Now that lines have types, group them. This could have done this
        # above, but functinoality is split for readability.
        prev_source = None
        grouped_lines = []
        for state, group in it.groupby(labeled_lines, lambda t: t[0]):
            block = [t[1] for t in group]
            if state == 'text':
                if prev_source is not None:
                    # accept a source block without a want block
                    grouped_lines.append((prev_source, ''))
                    prev_source = None
                # accept the text
                grouped_lines.append(block)
            elif state == 'want':
                assert prev_source is not None, 'impossible'
                grouped_lines.append((prev_source, block))
                prev_source = None
            elif state == 'dsrc':
                # need to check if there is a want after us
                prev_source = block
        # Case where last block is source
        if prev_source:
            grouped_lines.append((prev_source, ''))
        return grouped_lines

    def _locate_ps1_linenos(self, source_lines, line_indent):
        # Strip indentation (and PS1 / PS2 from source)
        norm_source_lines = [p[line_indent + 4:] for p in source_lines]
        source_block = '\n'.join(norm_source_lines)
        pt = ast.parse(source_block)
        ps1_linenos = [node.lineno - 1 for node in pt.body]
        NEED_16806_WORKAROUND = True
        if NEED_16806_WORKAROUND:
            ps1_linenos = self._workaround_16806(
                ps1_linenos, norm_source_lines)
        ps2_linenos = {
            x for x, p in enumerate(source_lines)
            if p[line_indent:line_indent + 4] != '>>> '
        }
        ps1_linenos = sorted(ps1_linenos.difference(ps2_linenos))
        return ps1_linenos

    def _workaround_16806(self, ps1_linenos, norm_source_lines):
        """
        workaround for python issue 16806 (https://bugs.python.org/issue16806)

        Issue causes lineno for multiline strings to give the line they end on, not
        the line they start on.  A patch for this issue exists
        `https://github.com/python/cpython/pull/1800`

        Notes:
            Starting from the end look at consecutive pairs of indices to inspect
            the statment it corresponds to.  (the first statment goes from
            ps1_linenos[-1] to the end of the line list.
        """
        new_ps1_lines = []
        b = len(norm_source_lines)
        for a in ps1_linenos[::-1]:
            # the position of `b` is correct, but `a` may be wrong
            # is_balanced will be False iff `a` is wrong.
            while not is_balanced(norm_source_lines[a:b]):
                # shift `a` down until it becomes correct
                a -= 1
            # push the new correct value back into the list
            new_ps1_lines.append(a)
            # set the end position of the next string to be `a` ,
            # note, because this `a` is correct, the next `b` is
            # must also be correct.
            b = a
        ps1_linenos = set(new_ps1_lines)
        return ps1_linenos

    def _label_docsrc_lines(self, string):
        """
        Example:
            >>> from xdoctest.doctest_parser import *
            >>> import textwrap
            >>> # Having multiline strings in doctests can be nice
            >>> string = textwrap.dedent(
                    '''
                    text
                    >>> items = ['also', 'nice', 'to', 'not', 'worry',
                    >>>          'about', '...', 'vs', '>>>']
                    ... print('but its still allowed')
                    but its still allowed

                    more text
                    ''').strip()
            >>> self = DoctestParser()
            >>> self._label_docsrc_lines(string)
            [('text', 'text'),
             ('dsrc', ">>> items = ['also', 'nice', 'to', 'not', 'worry', 'about',"),
             ('dsrc', ">>>          'using', '...', 'instead', 'of', '>>>']"),
             ('dsrc', "... print('but its still allowed')"),
             ('want', 'but its still allowed'),
             ('want', ''),
             ('want', 'more text')]
        """

        def _complete_source(line, state_indent, line_iter):
            """
            helper
            remove lines from the iterator if they are needed to complete source
            """

            norm_line = line[state_indent:]  # Normalize line indentation
            prefix = norm_line[:4]
            suffix = norm_line[4:]
            assert prefix.strip() in {'>>>', '...'}, '{}'.format(prefix)
            yield line

            source_parts = [suffix]
            while not is_balanced(source_parts):
                try:
                    linex, next_line = next(line_iter)
                except StopIteration:
                    raise SyntaxError('ill-formed doctest')
                norm_line = next_line[state_indent:]
                prefix = norm_line[:4]
                suffix = norm_line[4:]
                if prefix.strip() not in {'>>>', '...', ''}:  # nocover
                    raise SyntaxError(
                        'Bad indentation in doctest on line {}: {!r}'.format(
                            linex, next_line))
                source_parts.append(suffix)
                yield next_line

        # parse and differenatiate between doctest source and want statements.
        labeled_lines = []
        state_indent = 0

        # line states
        TEXT = 'text'
        DSRC = 'dsrc'
        WANT = 'want'

        # Move through states, keeping track of points where states change
        #     text -> [text, dsrc]
        #     dsrc -> [dsrc, want, text]
        #     want -> [want, text, dsrc]
        prev_state = TEXT
        curr_state = None
        line_iter = enumerate(string.splitlines())
        for linex, line in line_iter:
            match = _INDENT_RE.search(line)
            line_indent = 0 if match is None else (match.end() - match.start())
            norm_line = line[state_indent:]  # Normalize line indentation
            strip_line = line.strip()

            # Check prev_state transitions
            if prev_state == TEXT:
                # text transitions to source whenever a PS1 line is encountered
                # the PS1(>>>) can be at an arbitrary indentation
                if strip_line.startswith('>>> '):
                    curr_state = DSRC
                else:
                    curr_state = TEXT
            elif prev_state == WANT:
                # blank lines terminate wants
                if len(strip_line) == 0:
                    curr_state = TEXT
                # source-inconsistent indentation terminates want
                elif line.strip().startswith('>>> '):
                    curr_state = DSRC
                elif line_indent < state_indent:
                    curr_state = TEXT
                else:
                    curr_state = WANT
            elif prev_state == DSRC:
                if len(strip_line) == 0 or line_indent < state_indent:
                    curr_state = TEXT
                # allow source to continue with either PS1 or PS2
                elif norm_line.startswith(('>>> ', '... ')):
                    if strip_line == '...':
                        curr_state = WANT
                    else:
                        curr_state = DSRC
                else:
                    curr_state = WANT

            # Handle transitions
            if prev_state != curr_state:
                # Handle start of new states
                if curr_state == TEXT:
                    state_indent = 0
                if curr_state == DSRC:
                    # Start a new source
                    state_indent = line_indent
                    # renormalize line when indentation changes
                    norm_line = line[state_indent:]

            # continue current state
            if curr_state == DSRC:
                # source parts may consume more than one line
                for part in _complete_source(line, state_indent, line_iter):
                    labeled_lines.append((DSRC, part))
            elif curr_state == WANT:
                labeled_lines.append((WANT, line))
            elif curr_state == TEXT:
                labeled_lines.append((TEXT, line))
            prev_state = curr_state

        return labeled_lines


def is_balanced(lines):
    """
    Checks if the lines have balanced parens, brakets, curlies and strings

    Args:
        lines (list): list of strings

    Returns:
        bool : True if statment has balanced containers

    Doctest:
        >>> assert is_balanced(['print(foobar)'])
        >>> assert is_balanced(['foo = bar']) is True
        >>> assert is_balanced(['foo = (']) is False
        >>> assert is_balanced(['foo = (', "')(')"]) is True
        >>> assert is_balanced(
        ...     ['foo = (', "'''", ")]'''", ')']) is True
    """
    if sys.version_info.major == 3:
        block = '\n'.join(lines)
    else:
        block = '\n'.join(lines).encode('utf8')
    stream = StringIO()
    stream.write(block)
    stream.seek(0)
    try:
        for t in tokenize.generate_tokens(stream.readline):
            pass
    except tokenize.TokenError as ex:
        message = ex.args[0]
        if message.startswith('EOF in multi-line'):
            return False
        raise
    else:
        return True


def min_indentation(s):
    "Return the minimum indentation of any non-blank line in `s`"
    indents = [len(indent) for indent in _INDENT_RE.findall(s)]
    if len(indents) > 0:
        return min(indents)
    else:
        return 0
