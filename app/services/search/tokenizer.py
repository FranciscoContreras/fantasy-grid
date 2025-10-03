"""
Text tokenization and analysis for search engine.
Handles tokenization, stopword removal, and stemming.
"""
import re
from typing import List

# Porter Stemmer implementation
class PorterStemmer:
    """
    Python implementation of Porter Stemming Algorithm
    Based on the original algorithm by Martin Porter
    """

    def __init__(self):
        self.vowels = 'aeiou'
        self.consonants = 'bcdfghjklmnpqrstvwxyz'

    def _is_consonant(self, word: str, i: int) -> bool:
        """Check if character at position i is a consonant"""
        if i < 0 or i >= len(word):
            return False

        char = word[i]
        if char in self.vowels:
            return False
        if char == 'y':
            if i == 0:
                return True
            return not self._is_consonant(word, i - 1)
        return True

    def _measure(self, word: str) -> int:
        """Calculate the measure of a word (number of VC sequences)"""
        measure = 0
        i = 0
        length = len(word)

        # Skip initial consonants
        while i < length and self._is_consonant(word, i):
            i += 1

        # Count VC sequences
        while i < length:
            # Skip vowels
            while i < length and not self._is_consonant(word, i):
                i += 1
            if i >= length:
                break
            measure += 1
            # Skip consonants
            while i < length and self._is_consonant(word, i):
                i += 1

        return measure

    def _contains_vowel(self, word: str) -> bool:
        """Check if word contains a vowel"""
        for i in range(len(word)):
            if not self._is_consonant(word, i):
                return True
        return False

    def _ends_double_consonant(self, word: str) -> bool:
        """Check if word ends with double consonant"""
        if len(word) < 2:
            return False
        return (word[-1] == word[-2] and
                self._is_consonant(word, len(word) - 1))

    def _ends_cvc(self, word: str) -> bool:
        """Check if word ends with consonant-vowel-consonant pattern"""
        if len(word) < 3:
            return False

        i = len(word) - 1
        if not self._is_consonant(word, i):
            return False
        if word[i] in 'wxy':
            return False
        if self._is_consonant(word, i - 1):
            return False
        if not self._is_consonant(word, i - 2):
            return False
        return True

    def _replace_suffix(self, word: str, old: str, new: str, min_measure: int = 0) -> str:
        """Replace suffix if measure condition is met"""
        if word.endswith(old):
            stem = word[:-len(old)]
            if self._measure(stem) > min_measure:
                return stem + new
        return word

    def stem(self, word: str) -> str:
        """Apply Porter stemming algorithm to a word"""
        if len(word) <= 2:
            return word

        word = word.lower()

        # Step 1a: plurals and -ed, -ing
        if word.endswith('sses'):
            word = word[:-2]
        elif word.endswith('ies'):
            word = word[:-2]
        elif word.endswith('ss'):
            pass
        elif word.endswith('s'):
            word = word[:-1]

        # Step 1b
        if word.endswith('eed'):
            stem = word[:-3]
            if self._measure(stem) > 0:
                word = stem + 'ee'
        elif word.endswith('ed'):
            stem = word[:-2]
            if self._contains_vowel(stem):
                word = stem
                # Apply additional rules
                if word.endswith('at'):
                    word += 'e'
                elif word.endswith('bl'):
                    word += 'e'
                elif word.endswith('iz'):
                    word += 'e'
                elif self._ends_double_consonant(word) and word[-1] not in 'lsz':
                    word = word[:-1]
                elif self._measure(word) == 1 and self._ends_cvc(word):
                    word += 'e'
        elif word.endswith('ing'):
            stem = word[:-3]
            if self._contains_vowel(stem):
                word = stem
                if word.endswith('at'):
                    word += 'e'
                elif word.endswith('bl'):
                    word += 'e'
                elif word.endswith('iz'):
                    word += 'e'
                elif self._ends_double_consonant(word) and word[-1] not in 'lsz':
                    word = word[:-1]
                elif self._measure(word) == 1 and self._ends_cvc(word):
                    word += 'e'

        # Step 1c
        if word.endswith('y'):
            stem = word[:-1]
            if self._contains_vowel(stem):
                word = stem + 'i'

        # Step 2
        if len(word) > 3:
            second_step = {
                'ational': 'ate', 'tional': 'tion', 'enci': 'ence',
                'anci': 'ance', 'izer': 'ize', 'abli': 'able',
                'alli': 'al', 'entli': 'ent', 'eli': 'e',
                'ousli': 'ous', 'ization': 'ize', 'ation': 'ate',
                'ator': 'ate', 'alism': 'al', 'iveness': 'ive',
                'fulness': 'ful', 'ousness': 'ous', 'aliti': 'al',
                'iviti': 'ive', 'biliti': 'ble'
            }
            for suffix, replacement in second_step.items():
                if word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    if self._measure(stem) > 0:
                        word = stem + replacement
                    break

        # Step 3
        if len(word) > 3:
            third_step = {
                'icate': 'ic', 'ative': '', 'alize': 'al',
                'iciti': 'ic', 'ical': 'ic', 'ful': '',
                'ness': ''
            }
            for suffix, replacement in third_step.items():
                if word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    if self._measure(stem) > 0:
                        word = stem + replacement
                    break

        # Step 4
        if len(word) > 3:
            fourth_step = [
                'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible',
                'ant', 'ement', 'ment', 'ent', 'ion', 'ou', 'ism',
                'ate', 'iti', 'ous', 'ive', 'ize'
            ]
            for suffix in fourth_step:
                if word.endswith(suffix):
                    stem = word[:-len(suffix)]
                    if suffix == 'ion' and len(stem) > 0 and stem[-1] in 'st':
                        if self._measure(stem) > 1:
                            word = stem
                    elif self._measure(stem) > 1:
                        word = stem
                    break

        # Step 5a
        if word.endswith('e'):
            stem = word[:-1]
            measure = self._measure(stem)
            if measure > 1:
                word = stem
            elif measure == 1 and not self._ends_cvc(stem):
                word = stem

        # Step 5b
        if (self._measure(word) > 1 and
            self._ends_double_consonant(word) and
            word[-1] == 'l'):
            word = word[:-1]

        return word


# Stopwords list
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
    'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how',
    'all', 'each', 'she', 'or', 'can', 'if', 'no', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'just', 'should'
}


class TextAnalyzer:
    """Analyzes and tokenizes text for search indexing"""

    def __init__(self):
        self.stemmer = PorterStemmer()

    def tokenize(self, text: str) -> List[str]:
        """Split text into tokens (words)"""
        # Remove special characters and split on whitespace
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()
        return [t for t in tokens if t]  # Remove empty strings

    def lowercase_filter(self, tokens: List[str]) -> List[str]:
        """Convert all tokens to lowercase"""
        return [token.lower() for token in tokens]

    def stopword_filter(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from tokens"""
        return [token for token in tokens if token not in STOPWORDS]

    def stem_filter(self, tokens: List[str]) -> List[str]:
        """Apply stemming to tokens"""
        return [self.stemmer.stem(token) for token in tokens]

    def analyze(self, text: str) -> List[str]:
        """
        Complete analysis pipeline:
        1. Tokenize
        2. Lowercase
        3. Remove stopwords
        4. Stem words
        """
        tokens = self.tokenize(text)
        tokens = self.lowercase_filter(tokens)
        tokens = self.stopword_filter(tokens)
        tokens = self.stem_filter(tokens)
        return tokens


# Singleton instance
_analyzer = None

def get_analyzer() -> TextAnalyzer:
    """Get or create the text analyzer singleton"""
    global _analyzer
    if _analyzer is None:
        _analyzer = TextAnalyzer()
    return _analyzer


def analyze_text(text: str) -> List[str]:
    """Convenience function to analyze text"""
    return get_analyzer().analyze(text)
