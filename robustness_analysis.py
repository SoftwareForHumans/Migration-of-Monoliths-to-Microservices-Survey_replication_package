#!/usr/bin/env python3
"""Robustness analysis for the survey data.

Complements the descriptive analysis in analysis.ipynb by assessing how much
confidence the reported findings warrant:
  1. 95% Wilson confidence intervals for the main reported proportions.
  2. Exploratory subgroup association analyses (Fisher's exact tests with
     Benjamini-Hochberg correction): experience, project size, domain, and
     geography vs. tool adoption, migration strategy, and evaluation practice.
  3. Sensitivity analysis tables: main proportions on the full sample,
     excluding Brazil-based respondents, and excluding Finance-domain projects.

Pure standard-library implementation (no scipy/pandas required).
Usage: python3 robustness_analysis.py
"""

import csv
import math
from collections import Counter

DATA = "survey_responses_cleaned.csv"

# ---------------------------------------------------------------- statistics


def wilson_ci(k, n, z=1.959964):
    """95% Wilson score interval for a binomial proportion."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def fisher_exact_two_sided(a, b, c, d):
    """Two-sided Fisher's exact test p-value for the 2x2 table [[a,b],[c,d]].

    Sums the probabilities of all tables (with the same margins) whose
    point probability does not exceed that of the observed table.
    """
    row1, row2 = a + b, c + d
    col1 = a + c
    n = row1 + row2

    def p_table(x):  # hypergeometric point probability with a = x
        return (
            math.comb(row1, x)
            * math.comb(row2, col1 - x)
            / math.comb(n, col1)
        )

    lo = max(0, col1 - row2)
    hi = min(col1, row1)
    p_obs = p_table(a)
    eps = 1e-12
    return min(1.0, sum(p_table(x) for x in range(lo, hi + 1)
                        if p_table(x) <= p_obs + eps))


def benjamini_hochberg(pvals):
    """Return BH-adjusted p-values (q-values), preserving input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank_from_end, idx in enumerate(reversed(order)):
        rank = m - rank_from_end
        q = min(prev, pvals[idx] * m / rank)
        adj[idx] = q
        prev = q
    return adj


# ---------------------------------------------------------------- load data

with open(DATA, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

N = len(rows)
assert N == 65, f"expected 65 valid responses, found {N}"


def col(i):
    return [r[i] for r in rows]


# Column indices (see survey_instrument.pdf / header of the CSV)
C_COUNTRY, C_YEARS, C_PROJECTS, C_USERS, C_TEAM = 3, 4, 5, 7, 8
C_GUIDANCE, C_STRATEGY, C_CRITERIA, C_TOOLS_USED = 9, 10, 15, 16
C_LIKERT_MONO = {"Strangler Fig": 21, "UI Composition": 22,
                 "Branch by Abstraction": 23, "Parallel Run": 24,
                 "Decorating Collaborator": 25, "Change Data Capture": 26,
                 "Change code dependency to service call": 27}
C_LIKERT_DB = {"Database View": 30, "Database Wrapping Service": 31,
               "Database-as-a-Service Interface": 32,
               "Aggregate Exposing the Monolith": 33,
               "Change Data Ownership": 34,
               "Synchronize Data in Application": 35, "Tracer Write": 36,
               "Split Table": 37, "Move Foreign-Key Relationship to Code": 38}
C_DOMAINS, C_CHALLENGES, C_QUALITY, C_ENVS, C_INPUTS = 6, 42, 44, 47, 48

# ------------------------------------------------------ respondent subgroups

is_brazil = [c.strip() == "Brazil" for c in col(C_COUNTRY)]
is_finance = ["financ" in d.lower() for d in col(C_DOMAINS)]
years = [float(y) for y in col(C_YEARS)]
projects = [float(p) for p in col(C_PROJECTS)]
exp_high = [y > 5 for y in years]              # more than 5 years
proj_high = [p >= 3 for p in projects]         # 3 or more migration projects
team_large = [t.strip() in ("50 – 200", "200 – 600", "> 600")
              for t in col(C_TEAM)]            # 50+ people
users_large = [u.strip() in ("100K – 1M", "> 1M")
               for u in col(C_USERS)]          # 100K+ monthly active users

# ------------------------------------------------------------------ outcomes

used_tools = [v.strip() == "Yes" for v in col(C_TOOLS_USED)]
strat_continuous = ["Continuous refactoring interspersed with product evolution"
                    in v for v in col(C_STRATEGY)]
strat_rewrite = ["Rewrite/rebuild the entire system from scratch" in v
                 for v in col(C_STRATEGY)]
eval_production = ["Production" in v for v in col(C_ENVS)]


def agree(i):
    return [v.strip() in ("Agree", "Strongly Agree", "Strongly agree")
            for v in col(i)]


# ------------------------------------------------- headline proportions (CI)

headline = [
    ("Never used migration tools", [not t for t in used_tools]),
    ("Strategy: continuous refactoring", strat_continuous),
    ("Strategy: rewrite from scratch", strat_rewrite),
    ("Boundary criterion: by subdomain",
     ["subdomain" in v.lower() for v in col(C_CRITERIA)]),
    ("Boundary criterion: by business capability",
     ["business capabilit" in v.lower() for v in col(C_CRITERIA)]),
    ("Guidance: web resources and blogs",
     ["Web resources" in v or "blogs" in v.lower() for v in col(C_GUIDANCE)]),
    ("Guidance: scientific articles",
     ["cientific" in v for v in col(C_GUIDANCE)]),
    ("Technique: Strangler Fig (agree/strongly agree)",
     agree(C_LIKERT_MONO["Strangler Fig"])),
    ("Technique: Change Data Ownership (agree/strongly agree)",
     agree(C_LIKERT_DB["Change Data Ownership"])),
    ("Challenge: database migration and data store splitting",
     ["atabase migration" in v for v in col(C_CHALLENGES)]),
    ("Challenge: dealing with data consistency",
     ["data consistency" in v.lower() for v in col(C_CHALLENGES)]),
    ("Quality attribute: scalability (= efficiency, performance)",
     ["Scalability" in [p.strip() for p in v.split(",")]
      for v in col(C_QUALITY)]),
    ("Evaluates in development environment",
     ["Development" in v for v in col(C_ENVS)]),
    ("Evaluates in production environment", eval_production),
    ("Input: functional tests",
     ["unctional test" in v for v in col(C_INPUTS)]),
]

print("=" * 78)
print("1. HEADLINE PROPORTIONS WITH 95% WILSON CONFIDENCE INTERVALS (n=65)")
print("=" * 78)
for name, flags in headline:
    k = sum(flags)
    lo, hi = wilson_ci(k, N)
    print(f"{name:<58s} {k:>2d}/{N}  {k/N:6.1%}  [{lo:5.1%}, {hi:5.1%}]")

# --------------------------------------------------- subgroup associations

factors = [
    ("Experience > 5 years", exp_high),
    ("3+ migration projects", proj_high),
    ("Team of 50+ people", team_large),
    ("100K+ monthly active users", users_large),
    ("Finance domain", is_finance),
    ("Based in Brazil", is_brazil),
]
outcomes = [
    ("Used migration tools", used_tools),
    ("Continuous-refactoring strategy", strat_continuous),
    ("Evaluates in production", eval_production),
]

tests = []
for oname, ovals in outcomes:
    for fname, fvals in factors:
        a = sum(1 for o, fl in zip(ovals, fvals) if o and fl)
        b = sum(1 for o, fl in zip(ovals, fvals) if o and not fl)
        c = sum(1 for o, fl in zip(ovals, fvals) if not o and fl)
        d = sum(1 for o, fl in zip(ovals, fvals) if not o and not fl)
        p = fisher_exact_two_sided(a, b, c, d)
        n_f, n_nf = a + c, b + d
        tests.append((oname, fname, a, n_f, b, n_nf, p))

qvals = benjamini_hochberg([t[-1] for t in tests])

print()
print("=" * 78)
print("2. EXPLORATORY SUBGROUP ASSOCIATIONS (Fisher's exact, BH-adjusted)")
print("=" * 78)
print(f"{'Outcome':<32s}{'Factor':<28s}{'yes|factor':>11s}"
      f"{'yes|other':>11s}{'p':>8s}{'q(BH)':>8s}")
for (oname, fname, a, n_f, b, n_nf, p), q in zip(tests, qvals):
    print(f"{oname:<32s}{fname:<28s}{a:>4d}/{n_f:<4d}  {b:>4d}/{n_nf:<4d}"
          f"{p:>8.3f}{q:>8.3f}")

# --------------------------------------------------------- sensitivity table

subsets = [
    ("Full sample", [True] * N),
    ("Excluding Brazil", [not b for b in is_brazil]),
    ("Excluding Finance", [not f_ for f_ in is_finance]),
]

print()
print("=" * 78)
print("3. SENSITIVITY ANALYSIS: MAIN PROPORTIONS PER SUBSET")
print("=" * 78)
hdr = f"{'Finding':<58s}"
for sname, mask in subsets:
    hdr += f"{sname[:17]:>19s}"
print(hdr + "\n" + "-" * (58 + 19 * len(subsets)))
for name, flags in headline:
    line = f"{name:<58s}"
    for sname, mask in subsets:
        sel = [fl for fl, m in zip(flags, mask) if m]
        n_s = len(sel)
        line += f"{sum(sel):>4d}/{n_s:<3d}={sum(sel)/n_s:6.1%}   "
    print(line)
for sname, mask in subsets:
    print(f"  {sname}: n = {sum(mask)}")
