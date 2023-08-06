#!/usr/bin/env python

"""Check your CMS document against PubComm guidelines.

References:
https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PubGuidelines
https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PaperSubmissionPrep
https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PaperSubmissionFormat

Robin Aggleton 2018
robin dot aggleton at cern dot ch
"""

from __future__ import print_function
import os
import re
import sys
import json
import argparse
from collections import OrderedDict, defaultdict

from cmspubstyle.rules import normal_text
from cmspubstyle.rules import latex
from cmspubstyle.rules.classes import Location, ALL, ENVIRONMENT, INLINE, COMMAND
from cmspubstyle.rules.classes import Text, RuleBroken


ALL_RULES = normal_text.RULES + latex.RULES


class TERMCOL:
    """ASCII str for coloured/styled text in terminal shell"""
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def join_textlines(textlines):
    """Join the test in TextLines, removing newlines at end of lines"""
    return ''.join([x.text.rstrip('\n') for x in textlines])


def create_arg_parser():
    """Create an ArgumentParser"""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input",
                        help="Main paper/PAS/AN tex file. "
                        "Will also check every file included with \\input.")
    parser.add_argument("--doComments",
                        action='store_true',
                        help="Include comment lines in checks")
    return parser


def check_args(args):
    """Check all user arguments are sane, otherwise raise errors"""
    if not args.input.endswith(".tex"):
        raise RuntimeError("Your input file must be a .tex")

    if not os.path.isfile(args.input):
        raise IOError("Input file does not exist")


def extract_input_files(tex_file):
    """Return dict of included files in main tex file, split by category."""
    files_dict = OrderedDict()
    # the main tex file with abstract, title
    files_dict['root'] = tex_file
    # included bibliography
    files_dict['bib'] = os.path.splitext(tex_file)[0] + ".bib"

    # included files with main contents
    files_dict['contents'] = []
    input_pattern = re.compile(r"\\input\s*{(.+)}")
    with open(tex_file) as f:
        for line in f:
            if line.strip().startswith("%"):
                continue
            input_res = input_pattern.search(line)
            if not input_res:
                continue
            filename = input_res.group(1) + ".tex"
            filename = os.path.join(os.path.dirname(tex_file), filename)
            files_dict['contents'].append(filename)

    return files_dict


def report_error(broken_rule, color=TERMCOL.GREEN, padding=25):
    """Print broken rule message on screen, highlight violating part & rule"""
    # print(broken_rule)

    line_num_str = str(broken_rule.lines[0].line_num)
    if len(broken_rule.lines) > 1:
        line_num_str += " - " + str(broken_rule.lines[-1].line_num)

    match = broken_rule.match

    start_ind = match.start() - broken_rule.lines[0].char_num_start + 1
    end_ind = match.end() - broken_rule.lines[0].char_num_start + 1

    lines = ''.join([l.text for l in broken_rule.lines])

    quote_start = max(start_ind - padding, 0)
    quote_end = min(end_ind + padding, len(lines))
    error_str = lines[quote_start:start_ind].lstrip()
    error_str += color + TERMCOL.UNDERLINE + TERMCOL.BOLD + match.group(0) + TERMCOL.ENDC
    error_str += lines[end_ind:quote_end]
    error_str = error_str.rstrip()

    print("  L" + line_num_str + ":", error_str,
          TERMCOL.PINK, "[", broken_rule.rule.description, "]",
          TERMCOL.ENDC)


def check_text(text, do_comments):
    """Method to check any piece of main text (not bib)"""
    # locations = list(set([rule.where for rule in chain(normal_text.rules, latex.rules)]))
    # for l in locations:
    #     print(l)

    # for x in text.text_contents:
    #     print(x)
    # print(text.text_as_one_line)

    for rule in ALL_RULES:
        where = rule.where
        if isinstance(where, Location):
            where = [rule.where]

        for location in where:
            if isinstance(location, ALL):
                for match, lines in text.find_iter(rule.re_pattern):
                    # FIXME is this the best check? maybe check if any line?
                    if lines[0].text.strip().startswith("%") and not do_comments:
                        continue
                    yield RuleBroken(rule=rule, match=match, lines=lines)

            # elif isinstance(location, COMMAND):
            #     print('doing', location)
            #     for this_cmd_text in text.iter_command(location.opt):
            #         print(this_cmd_text)
            #         for match, lines in this_cmd_text.find_iter(rule.re_pattern):
            #             yield RuleBroken(rule=rule, match=match, lines=lines)

            # elif isinstance(location, INLINE):
            #     print('doing', location)
            #     for this_cmd_text in text.iter_inline_delim(location.opt):
            #         print(this_cmd_text)
            #         for match, lines in this_cmd_text.find_iter(rule.re_pattern):
            #             yield RuleBroken(rule=rule, match=match, lines=lines)

            # elif isinstance(location, ENVIRONMENT):
            #     print('doing', location)
            #     for this_cmd_text in text.iter_environment(location.opt):
            #         print(this_cmd_text)
            #         for match, lines in this_cmd_text.find_iter(rule.re_pattern):
            #             yield RuleBroken(rule=rule, match=match, lines=lines)


def check_and_report_errors(text, do_comments):
    """Check text for all errors, and print them out"""
    problems = []
    for broken_rule in check_text(text, do_comments):
        problems.append(broken_rule)
    problems = sorted(problems, key=lambda x: x.lines[0].line_num)
    for broken_rule in problems:
        report_error(broken_rule)
    return problems


def print_filename_header(filename):
    """Print header for filename"""
    separator = "-" * 60
    print(separator)
    print(TERMCOL.BLUE + filename + TERMCOL.ENDC)
    print(separator)


def check_root_file(filename):
    """Check elements of the main TeX file"""
    with open(filename) as f:
        root_text = Text(f.readlines())

    problems_dict = OrderedDict()

    abstract_text = list(root_text.iter_command("abstract"))[0]
    print_filename_header(filename + " (ABSTRACT)")
    abstract_problems = check_and_report_errors(abstract_text, do_comments=False)
    problems_dict[filename + " [ABSTRACT]"] = abstract_problems

    title_text = list(root_text.iter_command("title"))[0]
    print_filename_header(filename + " (TITLE)")
    title_problems = check_and_report_errors(title_text, do_comments=False)
    problems_dict[filename + " [TITLE]"] = title_problems

    return problems_dict


def check_content_files(filenames, do_comments=False):
    """Iterate through normal latex files and check each, printing out errors"""
    problems_dict = OrderedDict()
    for filename in filenames:
        with open(filename) as f:
            text = Text(f.readlines())
        print_filename_header(filename)
        these_problems = check_and_report_errors(text, do_comments)
        problems_dict[filename] = these_problems
    return problems_dict


# def check_bib_files(filenames):
#     return True


def print_final_summary(problems_dict, cached_results=None):
    """Print summary for user: # errors per file, and # per error type"""
    separator = "-" * 80
    print(separator)
    print(TERMCOL.YELLOW + TERMCOL.BOLD + "SUMMARY (by file)" + TERMCOL.ENDC)
    print(separator)
    max_len = max([len(f) for f in problems_dict])
    max_problems = max([len(p) for p in problems_dict.values()])
    max_problems_str = "%d" % max_problems
    for fname, problems in problems_dict.items():
        num_problems = len(problems)
        num_problems_str = str(num_problems)
        num_dots = max_len + 3 - len(fname) + len(max_problems_str) - len(num_problems_str)
        err_count_str = fname + "." * num_dots + num_problems_str
        # jsut skip if 0 problems?
        # this_col = bcolors.RED if num_problems > 0 else bcolors.GREEN

        # Print diff wrt cached results
        change = ""
        if cached_results:
            last_time = cached_results[fname]
            padding = "  "
            if num_problems > last_time:
                change = TERMCOL.RED + padding + "^"
            elif num_problems == last_time:
                change = TERMCOL.YELLOW + padding + "="
            else:
                change = TERMCOL.GREEN + padding + "v"
            change += " [was " + str(last_time) + "]" + TERMCOL.ENDC
        total_str = err_count_str + change
        print(total_str)

    print(separator)
    print(TERMCOL.YELLOW + TERMCOL.BOLD + "SUMMARY (by issue)" + TERMCOL.ENDC)
    print(separator)
    issue_dict = defaultdict(int)
    for problems in problems_dict.values():
        for problem in problems:
            issue_dict[problem.rule.description] += 1
    # Sort by descending # of occurences
    issue_dict = {k[0]: k[1] for k in sorted(issue_dict.items(), key=lambda x: x[1], reverse=True)}
    max_len = max([len(k) for k in issue_dict])
    desc_fmt_str = "{0:<%d}: " % (max_len+1)
    for desc, ind in issue_dict.items():
        print(desc_fmt_str.format(desc), ind)
    print(separator)
    total_num_issues = sum(issue_dict.values())
    total_num_bad_files = len([p for p in problems_dict if len(problems_dict[p]) > 0])
    print(TERMCOL.YELLOW + TERMCOL.BOLD + "TOTAL:",
          total_num_issues, "issues across", total_num_bad_files, "files",
          TERMCOL.ENDC)
    print(separator)


def read_results_from_cache(cache_filename, tex_filename):
    """Get cached results from JSON file"""
    if not os.path.isfile(cache_filename) or os.path.getsize(cache_filename) == 0:
        return None

    with open(cache_filename) as f:
        jdict = json.load(f)
        full_text_filename = os.path.abspath(tex_filename)
        if full_text_filename not in jdict:
            return None
        return jdict[full_text_filename]


def write_results_to_cache(results, cache_filename, tex_filename):
    """Save results to cache file for comparison on later runs"""
    full_text_filename = os.path.abspath(tex_filename)
    if os.path.isfile(cache_filename) and os.path.getsize(cache_filename) > 0:
        with open(cache_filename) as f:
            jdict = json.load(f)
    else:
        jdict = {full_text_filename: None}

    slim_results = {k: len(v) for k, v in results.items()}
    jdict[full_text_filename] = slim_results

    with open(cache_filename, 'w') as f:
        json.dump(jdict, f, indent=2)


def main(in_args):
    """Main function to organise all the things, collate results, publish them"""
    parser = create_arg_parser()
    args = parser.parse_args(in_args)
    check_args(args)

    print("Checking against", len(ALL_RULES), "rules")

    cache_filename = "checker_cache.json"
    cached_results = read_results_from_cache(cache_filename, args.input)

    files_dict = extract_input_files(args.input)
    root_results = check_root_file(files_dict['root'])
    content_results = check_content_files(files_dict['contents'], args.doComments)
    # bib_results = check_bib_files(files_dict['bib'])

    root_results.update(content_results)
    print_final_summary(root_results, cached_results)

    # write results to cache file
    write_results_to_cache(root_results, cache_filename, args.input)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
