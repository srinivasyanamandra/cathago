# core/utils/text_matching.py
import re
import math
import numpy as np
from collections import defaultdict, Counter 
from nltk.stem import PorterStemmer



# Basic Text Matching Functions
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def word_frequency(text):
    words = re.findall(r'\w+', text.lower())
    return Counter(words)

def text_similarity(text1, text2):
    distance = levenshtein_distance(text1, text2)
    freq1 = word_frequency(text1)
    freq2 = word_frequency(text2)
    common_words = set(freq1.keys()).intersection(set(freq2.keys()))
    similarity = sum(min(freq1[word], freq2[word]) for word in common_words) / max(sum(freq1.values()), sum(freq2.values()))
    return similarity, distance

# Enhanced Text Matching Functions
def tokenize_and_normalize(text):
    text = re.sub(r'[^\w\s]', '', text.lower())
    tokens = text.split()
    return tokens

STOP_WORDS = set(["the", "is", "and", "of", "in", "to", "a", "for"])

def remove_stop_words(tokens):
    return [word for word in tokens if word not in STOP_WORDS]

def stem_words(tokens):
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in tokens]

def calculate_tf(tokens):
    tf = defaultdict(int)
    for word in tokens:
        tf[word] += 1
    return tf

def calculate_idf(documents):
    idf = defaultdict(int)
    total_documents = len(documents)
    for doc in documents:
        unique_words = set(doc)
        for word in unique_words:
            idf[word] += 1
    for word, count in idf.items():
        idf[word] = math.log(total_documents / (1 + count))
    return idf

def calculate_tf_idf(tf, idf):
    tf_idf = {}
    for word, freq in tf.items():
        tf_idf[word] = freq * idf.get(word, 0)
    return tf_idf

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def enhanced_text_matching(doc1, doc2, all_documents):
    tokens1 = tokenize_and_normalize(doc1)
    tokens2 = tokenize_and_normalize(doc2)

    tokens1 = remove_stop_words(tokens1)
    tokens2 = remove_stop_words(tokens2)

    tokens1 = stem_words(tokens1)
    tokens2 = stem_words(tokens2)

    tf1 = calculate_tf(tokens1)
    tf2 = calculate_tf(tokens2)
    idf = calculate_idf(all_documents)
    tf_idf1 = calculate_tf_idf(tf1, idf)
    tf_idf2 = calculate_tf_idf(tf2, idf)

    all_words = set(tf_idf1.keys()).union(set(tf_idf2.keys()))
    vec1 = np.array([tf_idf1.get(word, 0) for word in all_words])
    vec2 = np.array([tf_idf2.get(word, 0) for word in all_words])

    similarity = cosine_similarity(vec1, vec2)
    return similarity