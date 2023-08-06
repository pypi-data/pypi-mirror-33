"""
For rules concerning normal text, like duplicate words, missing spaces.

"""

import re
from cmspubstyle.rules.classes import ALL, ENVIRONMENT, INLINE, COMMAND
from cmspubstyle.rules.classes import TestRule, Rule

RULES, TESTS = [], []

##############################################################################
# GENERAL
##############################################################################
RULES.append(
    Rule(description="Duplicate words",
         re_pattern=re.compile(r"\b(\w+)\b[\s.,]+\b\1\b", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=" .the THE "),
    TestRule(rule=RULES[-1], text=" ,the THE, "),
    TestRule(rule=RULES[-1], text=" the. THE "),
    TestRule(rule=RULES[-1], text=" the  THE "),
    TestRule(rule=RULES[-1], text=" the  THE,"),
    TestRule(rule=RULES[-1], text=" however, however "),
    TestRule(rule=RULES[-1], text=" the. Then ", should_pass=True),
])

# RULES.append(
#     Rule(description="Missing space at end of sentence",
#          re_pattern=re.compile(r"\.[A-Z]+"),
#          where=ALL())
# )
# TESTS.extend([
#     TestRule(rule=RULES[-1], text="blah.Blah"),
#     TestRule(rule=RULES[-1], text="v2.How"),
#     TestRule(rule=RULES[-1], text="v2.3", should_pass=True),
# ])

##############################################################################
# ABSTRACT ONLY
##############################################################################
RULES.append(
    Rule(description='Missing "LHC" in abstract',
         re_pattern=re.compile(r"^(?!.*LHC).*$"),
         where=COMMAND("abstract"))
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Some cool physics at ATLAS."),
    TestRule(rule=RULES[-1], text="Other physics at LHC. My cool result.", should_pass=True),
    TestRule(rule=RULES[-1], text="Other physics at LHC accelerator. My cool result.", should_pass=True),
])

RULES.append(
    Rule(description='Missing "CMS" in abstract',
         re_pattern=re.compile(r"^(?!.*CMS).*$"),
         where=COMMAND("abstract"))
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Some cool physics at ATLAS."),
    TestRule(rule=RULES[-1], text="Other physics at CMS. My cool result.", should_pass=True),
    TestRule(rule=RULES[-1], text="Other physics at CMS experiment. My cool result.", should_pass=True),
])

RULES.append(
    Rule(description='Missing Collaboration/experiment/detector after "CMS" in abstract',
         re_pattern=re.compile(r"CMS ((?!collaboration)(?!experiment))\w+", re.IGNORECASE),
         where=COMMAND("abstract"))
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Our CMS result"),
    TestRule(rule=RULES[-1], text="The CMS collaboration", should_pass=True),
])

RULES.append(
    Rule(description="Missing data year in abstract",
         re_pattern=re.compile(r"^(?!.*201[0-9]).*$",),
         where=COMMAND("abstract"))
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Our CMS result"),
    TestRule(rule=RULES[-1], text="Data taken in 2016", should_pass=True),
    TestRule(rule=RULES[-1], text="Data taken in 2016/2017", should_pass=True),
])

##############################################################################
# COMMAS
##############################################################################

RULES.append(
    Rule(description="No comma before et al",
         re_pattern=re.compile(r",\s\\etal"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Josie, \\etal"),
    TestRule(rule=RULES[-1], text="Mark  \\etal", should_pass=True),
])

##############################################################################
# HYPHENATION
##############################################################################
# UNHYPHENATED, 2 WORDS
UNHYPHENATED = [
    "b|jet",  # should hopefully catch \cPqb as well
    "b|quark",
    "b|tag",
    "b|tagging",
    "beam|halo",
    "black|hole",
    "g|jet",
    "g|quark",
    "g|tag",
    "g|tagging",
    "c|jet",
    "c|quark",
    "c|tag",
    "c|tagging",
    "s|jet",
    "s|quark",
    "s|tag",
    "s|tagging",
    "d|jet",
    "d|quark",
    "u|jet",
    "u|quark",
    "charged|particle",
    "colour|singlet",
    "cross|section",
    "heavy|ion",
    "Higgs|boson",
    "invariant|mass",
    "jet|energy",
    "jet|energy",
    # "$K$|factor",
    "lead|tungstate",
    "Monte|Carlo",
    "single|top",
    "standard|model",
    "tau|lepton",
    "top|quark",
    "W|boson",
    "Z|boson",
]

for word in UNHYPHENATED:
    pre, post = word.split("|")
    RULES.append(
        Rule(description="Unnecessary hyphenation",
             re_pattern=re.compile(pre+"-"+post+r"\b", re.IGNORECASE),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=pre+"-"+post),
        # TestRule(rule=RULES[-1], text=r"\cPQ"+pre+"-"+post),
        TestRule(rule=RULES[-1], text=pre+" "+post, should_pass=True),
        TestRule(rule=RULES[-1], text=pre+"  "+post, should_pass=True),
        TestRule(rule=RULES[-1], text="blahblah "+post, should_pass=True),
        TestRule(rule=RULES[-1], text=post+"ged", should_pass=True),
        # TestRule(rule=RULES[-1], text=r"\cPQ"+pre+" "+post, should_pass=True),
    ])

# UNHYPHENATED SINGLE WORDS

# SHOULD BE HYPHENATED
RULES.append(
    Rule(description="Missing hyphenation",
         re_pattern=re.compile(r" \w tagged", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=" b tagged"),
    TestRule(rule=RULES[-1], text=r"Higgs-tagged", should_pass=True),
    TestRule(rule=RULES[-1], text="the tagged", should_pass=True),
])


##############################################################################
# COMMON GRAMMATICAL MISTAKES
##############################################################################
RULES.append(
    Rule(description="Wrong indefinite article, 'SM' requires 'an'",
         re_pattern=re.compile(r"a SM", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="a SM"),
    TestRule(rule=RULES[-1], text=r"an SM", should_pass=True),
])

RULES.append(
    Rule(description="Wrong indefinite article, 'SUSY' requires 'a'",
         re_pattern=re.compile(r"\ban SUSY", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="an SUSY"),
    TestRule(rule=RULES[-1], text=r"a SUSY", should_pass=True),
])

RULES.append(
    Rule(description="'due to' or 'because of'?",
         re_pattern=re.compile(r"\bdue\b\s\bto", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="due to"),
    TestRule(rule=RULES[-1], text=r"subdue to", should_pass=True),
])

RULES.append(
    Rule(description="'evidence' takes no plural",
         re_pattern=re.compile(r"\bevidences", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=".Evidences"),
    TestRule(rule=RULES[-1], text="Evidences"),
    TestRule(rule=RULES[-1], text=r". Evidence for", should_pass=True),
])

RULES.append(
    Rule(description="'which' or 'that'?",
         re_pattern=re.compile(r"(?<!in)(?<!,) +\bwhich", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="background which"),
    TestRule(rule=RULES[-1], text="in which", should_pass=True),
    TestRule(rule=RULES[-1], text=r"background, which", should_pass=True),
])

RULES.append(
    Rule(description="Do not use \"it's\"",
         re_pattern=re.compile(r"\bit's", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="it's"),
    TestRule(rule=RULES[-1], text="bit's", should_pass=True),
    TestRule(rule=RULES[-1], text=r"nits", should_pass=True),
])

##############################################################################
# ACRONYMS
##############################################################################

RULES.append(
    Rule(description="Do not capitalise first letters",
         re_pattern=re.compile(r"Standard\b\s\bModel"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Standard Model"),
    TestRule(rule=RULES[-1], text="standard model", should_pass=True),
])

RULES.append(
    Rule(description="Do not capitalise first letters",
         re_pattern=re.compile(r"Quantum\b\s\bChromodynamics"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Quantum Chromodynamics"),
    TestRule(rule=RULES[-1], text="quantum chromodynamics", should_pass=True),
])

RULES.append(
    Rule(description="Do capitalise first letters",
         re_pattern=re.compile(r"monte\b\s\bcarlo"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="monte carlo"),
    TestRule(rule=RULES[-1], text="Monte Carlo", should_pass=True),
])

RULES.append(
    Rule(description="Do not use 'd.o.f' for degrees of freedom (use dof or n_d)",
         re_pattern=re.compile(r"d\.o\.f"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="d.o.f"),
    TestRule(rule=RULES[-1], text="dof", should_pass=True),
])

RULES.append(
    Rule(description="Do not start sentence with an acronym",
         re_pattern=re.compile(r"\.\s\b[A-Z]{2,}\b"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r". VLQ"),
    TestRule(rule=RULES[-1], text=".   VLQ"),
    TestRule(rule=RULES[-1], text=r"a QLZ", should_pass=True),
])

##############################################################################
# SYMBOLS
##############################################################################

RULES.append(
    Rule(description="Do not start sentence with a symbol",
         re_pattern=re.compile(r"\.\s[\$\\](?!section)(?!ref)(?!subsection)(?!item)(?!begin)(?!end)"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r". \Zp"),
    TestRule(rule=RULES[-1], text=".   $N_d$"),
    TestRule(rule=RULES[-1], text=r"a \QLZ", should_pass=True),
])

RULES.append(
    Rule(description="Use 'transverse momentum', not 'transverse energy'",
         re_pattern=re.compile(r"transverse\b\s\benergy", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"transverse  energy"),
    TestRule(rule=RULES[-1], text=r"transverse  momentum", should_pass=True),
])

##############################################################################
# WORD USE AND JARGON
##############################################################################

RULES.append(
    Rule(description="Avoid 'actual', prefer 'current'/'existing'",
         re_pattern=re.compile(r"\bactual\b", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the actual setup"),
    TestRule(rule=RULES[-1], text=r"factual", should_pass=True),
])

RULES.append(
    Rule(description="Use 'X antiquark', not 'antiX quark'",
         re_pattern=re.compile(r"\banti-?[\w]+\b\squark", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the antitop quark "),
    TestRule(rule=RULES[-1], text=r"the antibottom quark "),
    TestRule(rule=RULES[-1], text=r"the antitop quark's "),
    TestRule(rule=RULES[-1], text=r"the anti-top quark "),
    TestRule(rule=RULES[-1], text=r"the top antiquark", should_pass=True),
])

RULES.append(
    Rule(description="Use 'charged particle track' instead of 'charged track'",
         re_pattern=re.compile(r"\bcharged\b\s\btrack\b", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the charged track is"),
    TestRule(rule=RULES[-1], text=r"the charged   track."),
    TestRule(rule=RULES[-1], text=r"the charged tracking", should_pass=True), # why?
])

RULES.append(
    Rule(description="ATLAS & CMS Collaboration(s) have capital C",
         re_pattern=re.compile(r"(ATLAS|CMS)\b\s\bcollaboration"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the CMS collaboration"),
    TestRule(rule=RULES[-1], text=r"the ATLAS  collaboration."),
    TestRule(rule=RULES[-1], text=r"the ATLAS & CMS collaborations."),
    TestRule(rule=RULES[-1], text=r"then .ATLAS & CMS collaborations."),
    TestRule(rule=RULES[-1], text=r"the ATLAS and CMS Collaborations", should_pass=True),
])

RULES.append(
    Rule(description="Tevatron collaborations have lower case c",
         re_pattern=re.compile(r"\bTevatron\b\s\bCollaborations"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the Tevatron Collaborations"),
    TestRule(rule=RULES[-1], text=r"the Tevatron collaborations", should_pass=True),
])

RULES.append(
    Rule(description="D0 Collaboration has capital c",
         re_pattern=re.compile(r"\bD0\b\s\bcollaboration"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the D0 collaboration"),
    TestRule(rule=RULES[-1], text=r"the D0 Collaboration", should_pass=True),
])

RULES.append(
    Rule(description="Colloquial expression",
         re_pattern=re.compile(r"\bget\b\s\brid\b\s\bof", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"we get rid of background"),
    TestRule(rule=RULES[-1], text=r"forget riding off", should_pass=True),
])

RULES.append(
    Rule(description="'data' is plural",
         re_pattern=re.compile(r"\bdata\b\s\bis", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the data is good"),
    TestRule(rule=RULES[-1], text=r"the data isn't good"),
    TestRule(rule=RULES[-1], text=r" .Data    is"),
    TestRule(rule=RULES[-1], text=r"the data are", should_pass=True),
])

RULES.append(
    Rule(description="'data set' not 'dataset'",
         re_pattern=re.compile(r"\bdataset\b", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the dataset is good"),
    TestRule(rule=RULES[-1], text=r" .Data    set", should_pass=True),
    TestRule(rule=RULES[-1], text=r"the data set", should_pass=True),
])

SHOULD_BE_FOLLOWED = [
    ('Higgs', 'boson'),
    ('top', 'quark'),
    ('bottom', 'quark'),
    ('charm', 'quark'),
    ('strange', 'quark'),
    # ('up', 'quark'),   # these are hard, as many common cases, e.g. up to
    # ('down', 'quark'),
]
for first, second in SHOULD_BE_FOLLOWED:
    RULES.append(
        Rule(description="'"+first+"' should be followed by '"+second+"'",
             re_pattern=re.compile(r"\b"+first+r"\b\s*(?!"+second+r")[\w.']+", re.IGNORECASE),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=r"the "+first+" mass"),
        TestRule(rule=RULES[-1], text=r"the "+first+"."),
        TestRule(rule=RULES[-1], text=first+r" production"),
        TestRule(rule=RULES[-1], text=first+r" cross-section"),
        TestRule(rule=RULES[-1], text=r"the "+first+" "+second+" mass", should_pass=True),
    ])

SLANG_WORDS = [
    ('beamspot', 'luminous region/interaction point'),
    ('cut', 'criteria/requirement'),
    # ('dataset', 'data set'),
    # ('pileup', ''),
    ('fake', 'misidentified'),
    ('kinematics', 'kinematical variables'),
    ('statistics', 'more data/statistical precision'),
    ('systematics', 'systematic uncertainty/precision'),
    ('stop', 'top squark'),
    ('sbottom', 'bottom squark'),
    ('scharm', 'charm squark'),
    ('sstrange', 'strange squark'),
    ('sup', 'up squark'),
    ('sdown', 'down squark'),
]
for slang_word, better_word in SLANG_WORDS:
    RULES.append(
        Rule(description="Avoid '"+slang_word+"', prefer e.g. '"+better_word+"'",
             re_pattern=re.compile(r"(?<!:)\b"+slang_word+r"\b(?!})", re.IGNORECASE),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=r"the "+slang_word+" rate"),
        TestRule(rule=RULES[-1], text=r" ."+slang_word+"    ele"),
        TestRule(rule=RULES[-1], text=r"the f"+slang_word+"ery is", should_pass=True),
        TestRule(rule=RULES[-1], text=r"\ref{sec:"+slang_word+"}", should_pass=True),
    ])

DOUBLE_SLANG_WORDS = [
    ("coupling constant", "coupling strength"),
    ("Higgs tagging", "Higgs boson tagging/H tagging"),
    ("top tagging", "top quark tagging/t tagging"),
    ("uncertainty on", "uncertainty in"),
]
for slang_word, better_word in DOUBLE_SLANG_WORDS:
    parts = slang_word.split()
    RULES.append(
        Rule(description="Avoid '"+slang_word+"', instead '"+better_word+"'",
             re_pattern=re.compile(r"\b"+parts[0]+r"\b\s\b"+parts[1], re.IGNORECASE),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=r"the "+slang_word+" was"),
        TestRule(rule=RULES[-1], text=r"the "+slang_word.replace(" ", "    ")+"."),
        TestRule(rule=RULES[-1], text=r"the "+slang_word+"."),
        TestRule(rule=RULES[-1], text=r"."+slang_word+" was"),
        TestRule(rule=RULES[-1], text=r"the "+better_word+" was", should_pass=True),
    ])

RULES.append(
    Rule(description="Avoid 'error', instead 'uncertianty'",
         re_pattern=re.compile(r"\berror[s]?\b[\s\.]*?\b(?!bar)(?!band)[\w.']+", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the error was"),
    TestRule(rule=RULES[-1], text=r"the errors were"),
    TestRule(rule=RULES[-1], text=r"the error."),
    TestRule(rule=RULES[-1], text=r".Error was"),
    TestRule(rule=RULES[-1], text=r"-error time"),
    TestRule(rule=RULES[-1], text=r"the error bars", should_pass=True),
])

##############################################################################
# MISC
##############################################################################

LOWER_CASE = [
    'fermion',
    'boson',
]
for word in LOWER_CASE:
    upper_case = word[0].upper()+word[1:].lower()
    lower_case = word.lower()
    RULES.append(
        Rule(description="Do not capitalise first letter",
             re_pattern=re.compile(r"\b"+upper_case),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text="the "+upper_case),
        TestRule(rule=RULES[-1], text="the "+upper_case+"ic"),
        TestRule(rule=RULES[-1], text=". "+upper_case+"s"),
        TestRule(rule=RULES[-1], text="the "+lower_case+" stats", should_pass=True),
        TestRule(rule=RULES[-1], text="the "+lower_case+"ic", should_pass=True),
    ])

UPPER_CASE = [
    "Lagrangian",
    "Gaussian",
]
for word in UPPER_CASE:
    upper_case = word[0].upper()+word[1:].lower()
    lower_case = word.lower()
    RULES.append(
        Rule(description="Do capitalise first letter",
             re_pattern=re.compile(r"\b"+lower_case),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text="the "+lower_case),
        TestRule(rule=RULES[-1], text="the "+lower_case+"ic"),
        TestRule(rule=RULES[-1], text=". "+lower_case+"s"),
        TestRule(rule=RULES[-1], text="the "+upper_case+" stats", should_pass=True),
        TestRule(rule=RULES[-1], text="the "+upper_case+"ic", should_pass=True),
    ])

RULES.append(
    Rule(description="Use 'product of the cross section and branching'",
         re_pattern=re.compile(r"\bcross\b\s\bsection\b\s\btimes\b\s\bbranching\b", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the cross section times branching fraction is"),
    TestRule(rule=RULES[-1], text=r"the cross section times branching ratio is"),
    TestRule(rule=RULES[-1], text=r"the product of the cross section and branching fraction", should_pass=True),
])

RULES.append(
    Rule(description="Avoid indefinite article with '95% CL'",
         re_pattern=re.compile(r"\ba\b\s\b95\b\s*\\?\%\s*\\?CL", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"a 95% CL"),
    TestRule(rule=RULES[-1], text=r"a 95\% CL"),
    TestRule(rule=RULES[-1], text=r"a 95 \% CL"),
    TestRule(rule=RULES[-1], text=r"the 95% CL", should_pass=True),
    TestRule(rule=RULES[-1], text=r"the 95\% CL", should_pass=True),
    TestRule(rule=RULES[-1], text=r"the 95 \% CL", should_pass=True),
])


# For referring to sections, equations, etc there are several rules
# Some of these should never be abbreviated, others should
# Only capitalise when referring to a specific item
# Use a ~ to make sure line breaks dont damage it
# Same with citations
ALWAYS_FULL_WORD = [
    ('Tab.', 'Table'),
    ('Sec.', 'Section'),
    ('App.', 'Appendix'),
]

for short_word, full_word in ALWAYS_FULL_WORD:
    RULES.append(
        Rule(description="Do not abbreviate '"+full_word+"' to '"+short_word+"' when referencing that label",
             re_pattern=re.compile(r"\b"+short_word.replace(".", r"\."), re.IGNORECASE),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=short_word+r"~\ref{"),
        TestRule(rule=RULES[-1], text=r"the "+short_word),
        TestRule(rule=RULES[-1], text=r"the "+full_word+r"~\ref ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"\begin{"+full_word+r"~\ref ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+full_word+" shows", should_pass=True),
    ])

    # here we assume that the user refers to a Section etc with Section~\ref{...}
    RULES.append(
        Rule(description="Always capitalise '"+full_word+"' when referencing that label",
             re_pattern=re.compile(r"\b"+full_word.lower()+r"\b[~ ]\\ref"),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=full_word.lower()+r"~\ref{"),
        TestRule(rule=RULES[-1], text=" the "+full_word.lower()+r"~\ref{"),
        TestRule(rule=RULES[-1], text=r"the "+full_word.lower(), should_pass=True),
        TestRule(rule=RULES[-1], text=" the cross  "+full_word.lower()+r"~\cite{", should_pass=True),  # we're citing not ref-ing
        TestRule(rule=RULES[-1], text=r"\begin{"+full_word.lower()+r"}", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+full_word+r"~\ref ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"\sub"+full_word.lower()+r"{ ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+full_word+" shows", should_pass=True),
    ])


USE_ABBREVIATION = [
    ('Fig.', 'Figure'),
    ('Eq.', 'Equation'),
]

for short_word, full_word in USE_ABBREVIATION:
    RULES.append(
        Rule(description="Abbreviate '"+full_word+"' to '"+short_word+"' when referencing that label in sentence.",
             re_pattern=re.compile(r"(?<!\{figure\})(?<!\.)\s"+full_word+r"[ ~]?\\ref", re.IGNORECASE),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=r"the "+full_word+r"~\ref "),
        TestRule(rule=RULES[-1], text=r"the "+full_word+" shows", should_pass=True),  # ok to not abbreviate if no ref?
        TestRule(rule=RULES[-1], text=r"the "+short_word, should_pass=True),
        TestRule(rule=RULES[-1], text=r". "+full_word, should_pass=True),
        TestRule(rule=RULES[-1], text=r". "+full_word+" shows", should_pass=True),
        TestRule(rule=RULES[-1], text=r"\begin{"+full_word+r"~\ref ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"\begin{"+short_word+r"~\ref ", should_pass=True),
    ])

    RULES.append(
        Rule(description="Do not abbreviate '"+full_word+"' to '"+short_word+"' when referencing that label at start of sentence.",
             re_pattern=re.compile(r"\.\s"+short_word.replace(".", r"\.")+r"[ ~]?\\ref"),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=". "+short_word+r"~\ref{"),
        TestRule(rule=RULES[-1], text=r". "+full_word+r"~\ref{", should_pass=True),
    ])

    RULES.append(
        Rule(description="Always capitalise '"+full_word+"' when referencing that label",
             re_pattern=re.compile(r"(?<!{)(?<!\\)"+full_word.lower()+r"[ ~]?\\ref"),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=full_word.lower()+r"~\ref{"),
        TestRule(rule=RULES[-1], text=" the "+full_word.lower()+r"~\ref{"),
        TestRule(rule=RULES[-1], text=r"the "+full_word.lower()),
        TestRule(rule=RULES[-1], text=r". "+full_word.lower()),
        TestRule(rule=RULES[-1], text=r"."+full_word.lower()),
        TestRule(rule=RULES[-1], text=r"\begin{"+full_word.lower()+r"}", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+full_word+r"~\ref ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+full_word+" shows", should_pass=True),
        TestRule(rule=RULES[-1], text=r"abc"+full_word+"def", should_pass=True),
    ])

    RULES.append(
        Rule(description="Always capitalise '"+short_word+"'",
             re_pattern=re.compile(r"(?<!{)(?<!\\)"+short_word.lower().replace(".", r"\.")+r"[ ~]?\\ref"),
             where=ALL())
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=short_word.lower()+r"~\ref{"),
        TestRule(rule=RULES[-1], text=" the "+short_word.lower()+r"~\ref{"),
        TestRule(rule=RULES[-1], text=r"the "+short_word.lower()),
        TestRule(rule=RULES[-1], text=r"."+short_word.lower()),
        TestRule(rule=RULES[-1], text=r". "+short_word.lower()),
        TestRule(rule=RULES[-1], text=r"\begin{"+short_word.lower()+r"}", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+short_word+r"~\ref ", should_pass=True),
        TestRule(rule=RULES[-1], text=r"the "+short_word+" shows", should_pass=True),
        TestRule(rule=RULES[-1], text=r"abc"+short_word+"def", should_pass=True),
    ])
