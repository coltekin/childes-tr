#!/usr/bin/env python3

# This is an incomplete parser for childes CHAT files.

import sys, re

def parse_words(words):
    out = []
    for w in words:
        if w.startswith('&'):   # phonological forms
            continue
        x = w.replace('(', '').replace(')', '').replace('@q', '') # @q ismeta-lingustic use
        # skip all other special forms (@c @s etc.)
        if '@' in w or 'xxx' in w:  # skip unintelligible words too
            continue
        out.append(x)
    return out

def parse_chat(fp):
    """Parse and return a complete CHAT file"""
    utterances = []
    lines = fp.readlines()

    until_rbracket = re.compile("([^]]+)]")
    until_rangleb = re.compile("([^>]+)>")
    until_eow = re.compile("[^][,.;?!”<> ]+")
    punct_re = re.compile("([,.;?!:”])")

    utmp = ""
    i = 0
    while i < len(lines):
        if not lines[i].startswith("*"):
            i += 1
            continue
        utmp = lines[i].strip()
        i += 1
        while lines[i].startswith("\t"):
            utmp += " " + lines[i].strip()
            i += 1

        if utmp[6:].startswith('[- '):  # skip other languages
            continue
        u = {}
        u["speaker"] = utmp[1:4]
        j = 6
        words = []
        prev_tokens = []
        while j < len(utmp):
            if utmp[j].startswith(" "):
                j += 1
            elif utmp[j].startswith("<"):
                words.extend(prev_tokens)
                j += 1
                m = re.match(until_rangleb, utmp[j:])
                prev_tokens = m.group(1).strip().split()
                j += len(m.group(0))
            elif utmp[j:].startswith("[:: "): # std./correct spelling follows
                # discard the previous token(s)
                j += 4
                m = re.match(until_rbracket, utmp[j:])
                words.extend(m.group(1).strip().split())
                j += len(m.group(0))
                prev_tokens = []
            elif utmp[j:].startswith("[: "): # standard spelling follows
                # discard the previous token(s)
                j += 3
                m = re.match(until_rbracket, utmp[j:])
                words.extend(m.group(1).strip().split())
                j += len(m.group(0))
                prev_tokens = []
            elif utmp[j:].startswith("["): # we ignore others for now
                words.extend(prev_tokens)
                prev_tokens = []
                m = re.match(until_rbracket, utmp[j:])
                j += len(m.group(0))
            elif re.match(punct_re, utmp[j:]):
                words.extend(prev_tokens)
                prev_tokens = [utmp[j]]
                j += 1
            elif utmp[j:].startswith("“"): 
                words.extend(prev_tokens)
                prev_tokens = [utmp[j]]
                j += 1
            else: # a normal token
                words.extend(prev_tokens)
                m = re.match(until_eow, utmp[j:])
                prev_tokens = [m.group(0).strip()]
                j += len(m.group(0))
        words.extend(prev_tokens)
        u["words"] = parse_words(words)
        utterances.append(u)
    return utterances

for f in sys.argv[1:]:
    with open(f, "r") as fp:
        utrncs = parse_chat(fp)
        for u in utrncs:
            if len(u["words"]) == 0:
                continue
            print("{}: ".format(u["speaker"]), end="")
            for w in u["words"]:
                print("{} ".format(w), end="")
            print("")

