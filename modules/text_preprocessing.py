"""
text_preprocessing.py

Shared preprocessing used by BOTH document indexing and query handling.
This is the key fix: BM25 does exact token matching, so documents and
queries MUST be normalized the exact same way, or matches silently fail.

No new heavy dependencies required. We try nltk's PorterStemmer (pure
algorithmic, no data download needed) and fall back to a tiny rule-based
suffix stripper if nltk isn't installed, so this never breaks your app.
"""

import re

# ----------------------------------------------------------------------
# Demonym normalization
#
# ROOT CAUSE: Country fields store the noun ("India"), but users query
# with the adjective ("Indian"). "indian" != "india" as tokens, so no
# amount of stemming fixes this -- stemmers only strip suffixes like
# plurals/gerunds, they don't know nationality relationships. Without
# this step, the country term contributes ZERO to BM25 score, and
# ranking falls back entirely on other terms (e.g. "wicket keeper"),
# which is why non-Indian wicketkeepers were topping the "Indian
# wicket keeper" query.
#
# Multi-word demonyms (e.g. "West Indian", "South African") are listed
# BEFORE their shorter/overlapping counterparts and matched as phrases
# with word boundaries, so "west indian" -> "west indies" is applied
# before a generic "indian" -> "india" rule could incorrectly touch it.
# ----------------------------------------------------------------------
_DEMONYM_PATTERNS = [
    (r"\bwest indian(s)?\b", "west indies"),      # must precede plain "indian"
    (r"\bsouth african(s)?\b", "south africa"),
    (r"\bnew zealander(s)?\b", "new zealand"),
    (r"\bsri lankan(s)?\b", "sri lanka"),
    (r"\bindian(s)?\b", "india"),
    (r"\bpakistani(s)?\b", "pakistan"),
    (r"\baustralian(s)?\b", "australia"),
    (r"\benglish\b", "england"),
    (r"\bbangladeshi(s)?\b", "bangladesh"),
    (r"\bzimbabwean(s)?\b", "zimbabwe"),
    (r"\bafghan(i)?(s)?\b", "afghanistan"),
    (r"\bkiwi(s)?\b", "new zealand"),
    (r"\birish\b", "ireland"),
    (r"\bscottish\b", "scotland"),
    (r"\bwelsh\b", "wales"),
]

_COMPILED_DEMONYMS = [(re.compile(pat), repl) for pat, repl in _DEMONYM_PATTERNS]


def normalize_demonyms(text: str) -> str:
    """
    Replaces nationality adjectives with their country noun form.
    Runs on lowercased text, BEFORE tokenization, so both query and
    document text share the same vocabulary for country matching.
    """
    text = text.lower()
    for pattern, replacement in _COMPILED_DEMONYMS:
        text = pattern.sub(replacement, text)
    return text

# ----------------------------------------------------------------------
# Stemmer setup (handles "bowler" / "bowlers" / "bowling" -> same root)
# ----------------------------------------------------------------------
try:
    from nltk.stem import PorterStemmer
    _stemmer = PorterStemmer()

    def _stem(word: str) -> str:
        return _stemmer.stem(word)

except ImportError:
    # Fallback: minimal suffix-stripping stemmer, no dependency needed.
    # Not as linguistically accurate as Porter, but fixes the exact
    # singular/plural mismatch reported (bowler/bowlers, batsman/batsmen etc).
    def _stem(word: str) -> str:
        if len(word) <= 3:
            return word
        if word.endswith("ies"):
            return word[:-3] + "y"          # e.g. "centuries" -> "century"
        if word.endswith("ing") and len(word) > 5:
            return word[:-3]                # e.g. "bowling" -> "bowl"
        if word.endswith("es"):
            return word[:-2]                # e.g. "matches" -> "match"
        if word.endswith("s") and not word.endswith("ss"):
            return word[:-1]                # e.g. "bowlers" -> "bowler"
        return word


# ----------------------------------------------------------------------
# Optional lightweight stopword list (very common words carry ~zero
# BM25 IDF weight anyway, but stripping them keeps the token index smaller
# and slightly speeds up scoring)
# ----------------------------------------------------------------------
_STOPWORDS = {
    "a", "an", "the", "is", "was", "are", "were", "of", "in", "on",
    "and", "or", "to", "for", "with", "his", "her", "he", "she", "it",
}


# ----------------------------------------------------------------------
# Regex-based tokenizer (fixes item 1 & 3: strips punctuation, splits
# hyphenated terms like "right-arm" -> "right", "arm")
# ----------------------------------------------------------------------
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def clean_and_stem(text: str) -> list[str]:
    """
    Full preprocessing pipeline applied identically to documents and
    queries:
      1. Lowercase + normalize demonyms ("Indian" -> "india")
      2. Extract alphanumeric tokens only (strips punctuation/colons/commas)
      3. Drop stopwords
      4. Stem each token (collapses plurals / gerunds to a shared root)
    """
    text = normalize_demonyms(text)
    raw_tokens = _TOKEN_PATTERN.findall(text)
    tokens = [t for t in raw_tokens if t not in _STOPWORDS]
    return [_stem(t) for t in tokens]