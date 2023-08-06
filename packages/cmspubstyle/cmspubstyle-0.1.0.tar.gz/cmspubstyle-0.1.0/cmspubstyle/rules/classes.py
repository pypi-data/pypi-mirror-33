"""Classes to handle rules and test"""


import re
from bisect import bisect_left, bisect_right
from collections import namedtuple


def find_ge(sequence, item):
    'Find leftmost item greater than or equal to item'
    ind = bisect_left(sequence, item)
    if ind != len(sequence):
        return sequence[ind]
    raise ValueError


TextLine = namedtuple("TextLine", ["line_num", "char_num_start", "text"])


def cleanup_tex_line(text):
    """Format line of tex e.g. replace multiple spaces with one"""
    # replace multiple spaces with 1 space (simplifies matching)
    if text == r"\n":
        return ""
    text = re.sub(r" {2,}", " ", text)
    text = text.rstrip()
    return text


class Text(object):
    """Class to aid storage & finding in lines of latex"""

    def __init__(self, text, line_num_start=1):
        self.text_contents = []
        if text:
            # Creation from list of str
            if isinstance(text[0], str):
                for ind, line in enumerate(text, line_num_start):
                    # don't include the newline (which python counts as 1 char) since
                    # we remove it when searching, and it would screw up looking for
                    # relevant line(s)
                    char_num_start = sum([len(l.text) for l in self.text_contents]) + 1
                    this_line = line
                    this_line = cleanup_tex_line(this_line)
                    if (len(text) >= 2 and ind < (len(text)+line_num_start-1)
                            and (text[ind-line_num_start+1].rstrip() != "")):
                        this_line += " "  # latex auto adds a space. but only if text on next line
                    this_tl = TextLine(line_num=ind,
                                       char_num_start=char_num_start,
                                       text=this_line)
                    self.text_contents.append(this_tl)
            # Creation from list of TextLine e.g. from output of another Text
            elif type(text[0]) == TextLine:
                for line in text:
                    # reset char_num_start
                    char_num_start = 1 + sum([len(l.text.rstrip('\n'))
                                              for l in self.text_contents])
                    this_textline = TextLine(line_num=line.line_num,
                                             char_num_start=char_num_start,
                                             text=line.text)
                    self.text_contents.append(this_textline)
            else:
                raise RuntimeError("Unknown type %s for text arg for Text class "
                                   "- should be list[str] or list[TextLine]" % type(text[0]))

            self.text_as_one_line = ""
            self.create_one_str_from_contents()

    def create_one_str_from_contents(self):
        """Store text as one long line to make searching across lines easier"""
        self.text_as_one_line = ''.join([x.text.rstrip("\n") for x in self.text_contents])

    def find_line_with_char_num(self, char_num):
        """Select relevant line, based on which characters are involved"""
        # TODO: use bisect?
        for ind, line in enumerate(self.text_contents):
            if (line.char_num_start <= char_num and
                    (ind == len(self.text_contents)-1 or
                     self.text_contents[ind+1].char_num_start > char_num)):
                return line

    def find_lines_with_char_num_range(self, char_num_start, char_num_end):
        """Select lines based on range of character numbers"""
        char_num_starts = [x.char_num_start for x in self.text_contents]
        start_ind = bisect_right(char_num_starts, char_num_start)-1
        end_ind = bisect_left(char_num_starts, char_num_end)
        lines = self.text_contents[start_ind: end_ind]
        return lines

    def iter_environment(self, environment):
        r"""Return contents of environments, i.e. \begin{<environment>}...\end{<environment>}

        Returns list of TextLine for each occurence of \begin{<environment>}...\end{<environment>}
        """
        start_env = "\\begin{"+environment
        end_env = "\\end{"+environment
        if start_env not in self.text_as_one_line:
            yield None
            return
        # FIXME: this assumes everything on own lines,
        # no pre/post extra bits we dont want - issue?
        start_ind, end_ind = None, None
        for ind, line in enumerate(self.text_contents):
            if start_env in line.text:
                start_ind = ind
            if end_env in line.text:
                end_ind = ind
                if not (start_ind and end_ind):
                    raise RuntimeError("Found end of environment but not beginning: %s" % line)
                these_lines = self.text_contents[start_ind+1:end_ind]
                start_ind, end_ind = None, None
                yield Text(these_lines)

    def iter_inline_delim(self, delim="$"):
        """Iterate over text inside matching delim, e.g. $...$

        Returns TextLine for each occurence of <delim>...<delim>
        """
        matches = list(re.finditer("\\" + delim, self.text_as_one_line))
        print(matches)
        for match1, match2 in zip(matches[:-1:2], matches[1::2]):
            # Assumes all contents on one TextLine!
            line = self.find_line_with_char_num(match1.start()+1)
            # line2 = self.find_line_with_char_num(m2.end())
            # if l2.line_num != l.line_num:
            #     raise RuntimeError("Your inline maths spans 2 lines "
            #                        "- I don't knos how to handle that")
            this_text = self.text_as_one_line[match1.start()+1: match2.start()]
            # FIXME: what should char_num_start be doing?
            new_line = TextLine(line_num=line.line_num,
                                char_num_start=match1.start()+1,
                                text=this_text)
            yield Text([new_line])

    def iter_command(self, command):
        """Iterate over sections of text inside a \<command>{...}

        Returns list of TextLine for each occurence of \<command>
        """
        stack = []

        for match in re.finditer(r"\\"+command.lstrip("\\")+"{", self.text_as_one_line):
            # Use stack method to look for matching closing bracket
            # - could be more {} inside
            stack.append(match.end()-1)
            for char_ind, char in enumerate(self.text_as_one_line[match.end():], match.end()):
                if char == "{":
                    stack.append(char_ind)
                elif char == "}":
                    if len(stack) == 1:
                        start, end = stack.pop()+1, char_ind
                        # Handle the relevant line(s), chopping the text appropriately
                        these_lines = self.find_lines_with_char_num_range(start, end-1)

                        first_line_char_num = these_lines[0].char_num_start
                        offset_start = start - first_line_char_num + 1
                        these_lines[0] = TextLine(line_num=these_lines[0].line_num,
                                                  char_num_start=start+1,
                                                  text=these_lines[0].text[offset_start:])

                        last_line_char_num = these_lines[-1].char_num_start
                        offset_end = end - last_line_char_num + 1
                        these_lines[-1] = TextLine(line_num=these_lines[-1].line_num,
                                                   char_num_start=start,
                                                   text=these_lines[-1].text[:offset_end])
                        yield Text(these_lines)
                        break
                    else:
                        stack.pop()

    def find_iter(self, pattern):
        """Iterate over search results"""
        for match in pattern.finditer(self.text_as_one_line):
            # TODO what if >1 group?
            # matching_text = m.groups()

            # need the +1 on .start() as re uses 0-indexing, whilst .end() alread has +1
            start, end = match.start() + 1, match.end()
            lines = self.find_lines_with_char_num_range(start, end)
            yield (match, lines)


class Location(object):
    """Abstract base class for any section/type of text to be searched"""
    def __init__(self, opt=None):
        self.opt = opt

    def __hash__(self):
        return hash(self.opt)

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        return self.opt == other.opt

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        return not self.__eq__(other)

    def _to_str(self):
        """Common method to make str representation of classe for __str/repr__"""
        opt = "" if self.opt is None else self.opt
        return self.__class__.__name__+'('+opt+')'

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()


class ALL(Location):
    """All text including latex commands and environments"""
    def __init__(self, *args, **kwargs):
        super(ALL, self).__init__(*args, **kwargs)


class ENVIRONMENT(Location):
    """Only text within an environment e.g. \\begin{table}...\\end{table}"""
    def __init__(self, *args, **kwargs):
        super(ENVIRONMENT, self).__init__(*args, **kwargs)


class INLINE(Location):
    """Only text within an inline environment e.g. $...$"""
    def __init__(self, *args, **kwargs):
        super(INLINE, self).__init__(*args, **kwargs)


class COMMAND(Location):
    """Only text within a command e.g. \\text{...}"""
    def __init__(self, *args, **kwargs):
        super(COMMAND, self).__init__(*args, **kwargs)


# TODO: make this a namedtuple if only storing data fields?
class Rule(object):
    """Define an infraction, with human description, regex pattern, and location for infraction."""
    def __init__(self, description, re_pattern, where):
        self.description = description
        self.re_pattern = re_pattern
        self.where = where

    def __repr__(self):
        return "Rule("+str(self.re_pattern)+")"


class TestRule(object):
    """Class to define a test for a Rule, and whether it should pass or not"""

    def __init__(self, rule, text, should_pass=False):
        self.rule = rule
        if isinstance(text, str):
            self.text = Text([text])
        else:
            self.text = Text(text)
        self.should_pass = should_pass

    def _to_str(self):
        """Common method to make str representation of classe for __str/repr__"""
        str_args = {
            'rule': self.rule,
            'text': self.text.text_as_one_line,
            'should_pass': self.should_pass
        }
        return "TestRule(rule={rule}, text={text}, should_pass={should_pass})".format(**str_args)

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()

    # def test():
    #     result = True
    #     return result


# Handle a specific case of a rule being broken, the pure regex result, and the offending line(s)
RuleBroken = namedtuple("RuleBroken", ["rule", "match", "lines"])
