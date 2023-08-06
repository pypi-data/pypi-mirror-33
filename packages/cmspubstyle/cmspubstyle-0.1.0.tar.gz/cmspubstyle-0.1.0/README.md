# cmspubstyle

Check your PAS/PAPER/AN against the CMS PubComm guidelines.
Aims to make language review less embarrassing, since no one can remember several TWikis worth of somewhat arbitrary rules.

I bear no responsibility if this code misses errors.

## Install

Simply do:

```
pip install cmspubstyle
```

### Installation for development

If you want to install the package such that you can easily modify it, clone the git repository to a location of your choosing.
Then inside, run 

```
pip install -e .
```

## Running

Run with:

```
pubcheck.py <location of main TeX file>
```

The TeX file should be the top one for your paper, e.g. `B2G-17-015.tex`

## Add new rule

A rule is added via the `Rule` class.
Each rule is designed to look for **bad** words/patterns.
A rule has a `description`, which is presented to the user when an infraction occurs; therefore it should be concise and precise.
The matching pattern is implemented by a regular expression (in the form of a `re` pattern), passed in via the `re_pattern` arg.
Finally, the `where` arg specifies in what context to apply the rule: 

- `ALL()` for everywhere
- `ENVIRONMENT(xxx)` for sections inside `\begin{xxx}...\end{xxx}` (e.g. `ENVIRONMENT('figure')`)
- `INLINE(xxx)` for sections inside `xxx...xxx` (e.g. `INLINE('$')` for inline maths)
- `COMMAND(xxx)` for sections inside `\xxx{...}` (e.g. `COMMAND('abstract')` for the abstract)

A rule should have **at least 2** test cases: one case in which it fails the rule, and one case in which it passes the rule.
Tests for rules are implemented by instances of the `TestRule` class.
Each instance must have the `Rule` object which it is testing, the sample text string it is testing against, and whether or not the string should pass the rule (set via the `should_pass` arg).

The more test cases the better!

You should think about adding tests that cover a variety of scenarios: 

- what is the usual user error
- what are edge cases
- which correct texts might trigger the rule accidentally.

### Example rule and tests

An example is the following test for duplicate words (e.g. `The the fox jumped.`)

```python
rule = Rule(description="Duplicate words",
            re_pattern=re.compile(r"[\s.,](\w+)[\s.,]+\1[\s,.]+", re.IGNORECASE),
            where=ALL())

TestRule(rule=rule, text=" .the THE ")
TestRule(rule=rule, text=" ,the THE, ")
TestRule(rule=rule, text=" the. THE ")
TestRule(rule=rule, text=" the  THE ")
TestRule(rule=rule, text=" the  THE,")
TestRule(rule=rule, text=" however, however ")
TestRule(rule=rule, text=" the. Then ", should_pass=True)
```

The rule looks for a space/punctuation, at least one letter (i.e. a word), at least one space/punctuation, then the same "word", then space

Here you can see tests that cover:

- at the start of sentences
- split by punctuation
- in the middle of sentences
- more than one space between words
- a scenario in which there is not a duplicate (but almost)

and I'm still missing some scenarios!

## Running tests

To run the tests, you will need the `pytest` package.

If you do not already have it, install it with `pip install pytest`.

Then, just do `pytest`, and it will automatically run all tests.

## References

https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PubGuidelines

https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PaperSubmissionPrep

https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PaperSubmissionFormat
