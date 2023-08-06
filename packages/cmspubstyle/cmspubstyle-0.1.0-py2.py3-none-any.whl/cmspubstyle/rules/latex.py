"""
For rules concerning latex, like doing _{T}

"""

import re
from cmspubstyle.rules.classes import ALL, ENVIRONMENT, INLINE, COMMAND
from cmspubstyle.rules.classes import TestRule, Rule


# TODO check which of standard + new newcommands can be used e.g. \fbinv

RULES, TESTS = [], []

# This one is super tricky
# RULES.append(
#     Rule(description="Use roman subscript in maths",
#         # ignore if \mathrm or \text in subscript, but pickup other things
#          re_pattern=re.compile(r"[\w{}_\\=\[\].]*?_\{?(?!\\mathrm)(?!\\text)[\w\\]+\}?", re.IGNORECASE),
#          # re_pattern=re.compile(r"_\{?(?!\\mathrm)(?!\\text)[\w\\]+\}?", re.IGNORECASE),
#          # where=INLINE("$"))
#          where=ALL())
# )
# TESTS.extend([
#     TestRule(rule=RULES[-1], text="$p_T$"),
#     TestRule(rule=RULES[-1], text="$p_{V}$"),
#     TestRule(rule=RULES[-1], text="$p_{J2}$"),
#     TestRule(rule=RULES[-1], text="$p_{rec}$"),
#     TestRule(rule=RULES[-1], text="$p_{VLQ}$"),
#     TestRule(rule=RULES[-1], text=r"$p_{\Zp}$", should_pass=True),  # user macro
#     TestRule(rule=RULES[-1], text=r"$p_{\mathrm{T}}$", should_pass=True),
#     TestRule(rule=RULES[-1], text=r"$p_{\mathrm{T}}$", should_pass=True),
#     TestRule(rule=RULES[-1], text=r"$p_{\mathrm{rec}}$", should_pass=True),
# ])

RULES.append(
    Rule(description="Use \\ie macro",
         re_pattern=re.compile(r"i\.e\."),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="i.e."),
    TestRule(rule=RULES[-1], text=r"\ie", should_pass=True),
])

RULES.append(
    Rule(description="Use \\eg macro",
         re_pattern=re.compile(r"e\.g\."),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="e.g."),
    TestRule(rule=RULES[-1], text=r"\eg, he's a pain", should_pass=True),
])

RULES.append(
    Rule(description="Use \\etal macro",
         re_pattern=re.compile(r" et al"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Ram et al"),
    TestRule(rule=RULES[-1], text=r"Dave \etal", should_pass=True),
])

# DASHES
RULES.append(
    Rule(description="Use en dash -- for numerical range",
         re_pattern=re.compile(r"(?<![\w\d-])[\d.]+\s?(-|---)\s?[\d.]+"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="6-7"),
    # TestRule(rule=RULES[-1], text="-6-7"),  # FIXME how to handle this?
    TestRule(rule=RULES[-1], text="6.1-7.2"),
    TestRule(rule=RULES[-1], text="6 - 7"),
    TestRule(rule=RULES[-1], text="6---7"),
    TestRule(rule=RULES[-1], text="6 -- 7", should_pass=True),
    TestRule(rule=RULES[-1], text=r"\cite{CMS-PAS-17-01}", should_pass=True),
    TestRule(rule=RULES[-1], text="6--7", should_pass=True),
    TestRule(rule=RULES[-1], text="6.1--7.2", should_pass=True),
    # TestRule(rule=RULES[-1], text="-6.1--7.2", should_pass=True),  # FIXME how to handle this?
])

RULES.append(
    Rule(description="Use en dash -- for two people",
         re_pattern=re.compile(r"^((?!cite).)*?\b[A-Z][a-z]*\b\s?(-|---)\s?\b[A-Z][a-z]*\b"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text="Randall-Sundrum"),
    TestRule(rule=RULES[-1], text="Randall - Sundrum"),
    TestRule(rule=RULES[-1], text="Randall---Sundrum"),
    TestRule(rule=RULES[-1], text="Randall -- Sundrum", should_pass=True),
    TestRule(rule=RULES[-1], text="Randall--Sundrum", should_pass=True),
])

##############################################################################
# SYMBOLS
##############################################################################

RULES.append(
    Rule(description="Use 'anti-\\kt'",
         re_pattern=re.compile(r"anti\-(?!\\kt)\$?k"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"anti-k_{T}"),
    TestRule(rule=RULES[-1], text=r"anti-$k_{T}$"),
    TestRule(rule=RULES[-1], text=r"anti-\kt", should_pass=True),
    TestRule(rule=RULES[-1], text=r"anti-$\kt$", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\mathcal{B}' for branching fraction",
         re_pattern=re.compile(r"\bB\.?R\.?\b"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"the Z BR"),
    TestRule(rule=RULES[-1], text=r"the Z B.R."),
    TestRule(rule=RULES[-1], text=r"times \mathcal{B}", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\ptmiss' (without slash)",
         re_pattern=re.compile(r"\\PT(slash|m)"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"\PTslash"),
    TestRule(rule=RULES[-1], text=r"\PTm"),
    TestRule(rule=RULES[-1], text=r"\ptmiss", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\etmiss' (without slash)",
         re_pattern=re.compile(r"\\ETslash"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"\ETslash"),
    TestRule(rule=RULES[-1], text=r"\ETm", should_pass=True),
    TestRule(rule=RULES[-1], text=r"\etmiss", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\MeV' instead of 'MeV'",
         re_pattern=re.compile(r"(?<!\\)MeV"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"22MeV$"),
    TestRule(rule=RULES[-1], text=r"22 MeV$"),
    TestRule(rule=RULES[-1], text=r"22 MeVc$"),
    TestRule(rule=RULES[-1], text=r"22 MeVcc$"),
    TestRule(rule=RULES[-1], text=r"36\MeV", should_pass=True),
    TestRule(rule=RULES[-1], text=r"36\MeVc", should_pass=True),
    TestRule(rule=RULES[-1], text=r"36\MeVcc", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\GeV' instead of 'GeV'",
         re_pattern=re.compile(r"(?<!\\)GeV"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"22GeV$"),
    TestRule(rule=RULES[-1], text=r"22 GeV$"),
    TestRule(rule=RULES[-1], text=r"22 GeVc$"),
    TestRule(rule=RULES[-1], text=r"22 GeVcc$"),
    TestRule(rule=RULES[-1], text=r"36\GeV", should_pass=True),
    TestRule(rule=RULES[-1], text=r"36\GeVc", should_pass=True),
    TestRule(rule=RULES[-1], text=r"36\GeVcc", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\TeV' instead of 'TeV'",
         re_pattern=re.compile(r"(?<!\\)TeV"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"22TeV$"),
    TestRule(rule=RULES[-1], text=r"22 TeV$"),
    TestRule(rule=RULES[-1], text=r"22 TeVc$"),
    TestRule(rule=RULES[-1], text=r"22 TeVcc$"),
    TestRule(rule=RULES[-1], text=r"36\TeV", should_pass=True),
    TestRule(rule=RULES[-1], text=r"36\TeVc", should_pass=True),
    TestRule(rule=RULES[-1], text=r"36\TeVcc", should_pass=True),
])

RULES.append(
    Rule(description="Do not use '\\frac' inline, use '/'",
         # FIXME: make this INLINE
         re_pattern=re.compile(r"\\frac"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"$ a_{b} \frac{1}{2}$"),
    TestRule(rule=RULES[-1], text=r"1/2", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\fbinv' for luminosity",
         re_pattern=re.compile(r"1/fb"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"$36.5 1/fb$"),
    TestRule(rule=RULES[-1], text=r"36\fbinv", should_pass=True),
])

COMMON_FUNC_NAMES = ['sin', 'cos', 'tan', 'exp', 'log', 'ln']
for func_name in COMMON_FUNC_NAMES:
    RULES.append(
        Rule(description="Use macro '\\"+func_name+"'",
             re_pattern=re.compile(r"(?<!\\)"+func_name+r"[^\w\-]"),
             # re_pattern=re.compile(r"(?<!\\)"+func_name+r"\s*?(\\|\(|\[)"),
             where=ALL())
             # where=[INLINE("$"), COMMAND("EQUATION")])
    )
    TESTS.extend([
        TestRule(rule=RULES[-1], text=r"$\\times "+func_name+r"(x)$"),
        TestRule(rule=RULES[-1], text=r"$ "+func_name+r" x$"),
        TestRule(rule=RULES[-1], text=r"$ "+func_name+r" \\left(x$"),
        TestRule(rule=RULES[-1], text=r"$ "+func_name+r"\\phi$"),
        TestRule(rule=RULES[-1], text=r"$a \cdot \\"+func_name+r"(x)$", should_pass=True),
        TestRule(rule=RULES[-1], text=r" u"+func_name+r"g ", should_pass=True),
        TestRule(rule=RULES[-1], text=r" "+func_name+r"-normal ", should_pass=True),
        TestRule(rule=RULES[-1], text=r" "+func_name+r" normal", should_pass=True),
    ])

RULES.append(
    Rule(description="Use '\\begin{equation}...\\end{equation}' over '$$...$$'",
         re_pattern=re.compile(r"\$\$.*?\$\$"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"$$ a_{b} \\cdot d $$"),
    TestRule(rule=RULES[-1], text=r"$a b_{C}$", should_pass=True),
])

RULES.append(
    Rule(description="Prefer '\\to' over '\\rightarrow'",
         re_pattern=re.compile(r"\\rightarrow"),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"a \rightarrow b"),
    TestRule(rule=RULES[-1], text=r"a \to b$", should_pass=True),
])

RULES.append(
    Rule(description="Use '\\text{...}' not '{\\text...}'",
         re_pattern=re.compile(r"\{\\text[^{]*?\}", re.IGNORECASE),
         where=ALL())
)
TESTS.extend([
    TestRule(rule=RULES[-1], text=r"{\text abs}"),
    TestRule(rule=RULES[-1], text=r"\text{abs}", should_pass=True),
    TestRule(rule=RULES[-1], text=r"{\text{abs}}", should_pass=True),
])
