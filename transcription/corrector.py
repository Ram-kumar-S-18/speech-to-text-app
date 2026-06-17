import re


FILLERS = {
    r'\bum\b', r'\buh\b', r'\bhmm\b', r'\buhh\b',
    r'\bah\b', r'\bmm\b', r'\boh\b', r'\bhuh\b',
    r'\ber\b', r'\buhm\b', r'\bmmm\b',
}

FIXES = {
    "gonna": "going to", "wanna": "want to", "gotta": "got to",
    "lemme": "let me", "gimme": "give me", "kinda": "kind of",
    "sorta": "sort of", "dunno": "do not know",
    "cmon": "come on", "ima": "I am going to",
    "imma": "I am going to", "tryna": "trying to",
    "outta": "out of", "lotsa": "lots of",
    "coupla": "couple of", "lotta": "lot of",
    "yall": "you all", "dont": "do not",
    "dont": "do not", "doesnt": "does not",
    "isnt": "is not", "arent": "are not",
    "wont": "will not", "wouldnt": "would not",
    "couldnt": "could not", "shouldnt": "should not",
    "havent": "have not", "hasnt": "has not",
    "hadnt": "had not", "wasnt": "was not",
    "werent": "were not", "neednt": "need not",
    "cant": "cannot", "couldnt": "could not",
    "didnt": "did not", "doesnt": "does not",
    "its": "it is",
}

CONTRACTIONS = {
    r"\bi'm\b": "I am", r"\bi've\b": "I have",
    r"\bi'll\b": "I will", r"\bi'd\b": "I would",
    r"\byou're\b": "you are", r"\byou've\b": "you have",
    r"\byou'll\b": "you will", r"\byou'd\b": "you would",
    r"\bhe's\b": "he is", r"\bhe'll\b": "he will",
    r"\bhe'd\b": "he would",
    r"\bshe's\b": "she is", r"\bshe'll\b": "she will",
    r"\bshe'd\b": "she would",
    r"\bit's\b": "it is", r"\bit'll\b": "it will",
    r"\bit'd\b": "it would",
    r"\bwe're\b": "we are", r"\bwe've\b": "we have",
    r"\bwe'll\b": "we will", r"\bwe'd\b": "we would",
    r"\bthey're\b": "they are", r"\bthey've\b": "they have",
    r"\bthey'll\b": "they will", r"\bthey'd\b": "they would",
    r"\bthere's\b": "there is", r"\bthere'll\b": "there will",
    r"\bthere'd\b": "there would",
    r"\bthat's\b": "that is", r"\bthat'll\b": "that will",
    r"\bwhat's\b": "what is", r"\bwhat'll\b": "what will",
    r"\bwho's\b": "who is", r"\bwho'll\b": "who will",
    r"\bwhere's\b": "where is", r"\bhow's\b": "how is",
    r"\bhere's\b": "here is",
}

REPEATED_WORDS = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)
STUTTER = re.compile(r'\b(\w)\1{2,}\b')


class TranscriptCorrector:
    def correct(self, raw_text: str) -> str:
        if not raw_text or not raw_text.strip():
            return raw_text

        text = raw_text.strip()

        for pat in FILLERS:
            text = re.sub(pat, '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()

        for wrong, right in FIXES.items():
            text = re.sub(rf'\b{wrong}\b', right, text, flags=re.IGNORECASE)

        for pat, replacement in CONTRACTIONS.items():
            text = re.sub(pat, replacement, text, flags=re.IGNORECASE)

        for _ in range(3):
            new = REPEATED_WORDS.sub(r'\1', text)
            if new == text:
                break
            text = new

        text = STUTTER.sub(r'\1\1', text)

        if text and not text[-1] in '.!?':
            text += '.'
        text = re.sub(r'\s+\.', '.', text)
        text = re.sub(r'\s+,', ',', text)
        text = re.sub(r'\s+\?', '?', text)
        text = re.sub(r'\s+\!', '!', text)

        sentences = re.split(r'(?<=[.!?])\s+', text)
        fixed = []
        for s in sentences:
            s = s.strip()
            if s and s[0].islower():
                s = s[0].upper() + s[1:]
            fixed.append(s)

        result = ' '.join(fixed)

        result = result.replace(" .", ".").replace(" ,", ",")
        result = result.replace(" ?", "?").replace(" !", "!")

        return result
