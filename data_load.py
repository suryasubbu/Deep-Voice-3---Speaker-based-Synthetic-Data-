# -*- coding: utf-8 -*-
#/usr/bin/python2
'''
By kyubyong park. kbpark.linguist@gmail.com. 
https://www.github.com/kyubyong/deepvoice3
'''

from __future__ import print_function

from hyperparams import Hyperparams as hp
import numpy as np
import tensorflow as tf
from utils import *
import codecs
import re
import os
import unicodedata
from num2words import num2words

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

def text_normalize(sent):
    '''Minimum text preprocessing'''
    def _strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')

    normalized = []
    for word in sent.split():
        word = _strip_accents(word.lower())
        srch = re.match("\d[\d,.]*$", word)
        if srch:
            word = num2words(float(word.replace(",", "")))
        word = re.sub(u"[-—-]", " ", word)
        word = re.sub("[^ a-z'.?]", "", word)
        normalized.append(word)
    normalized = " ".join(normalized)
    normalized = re.sub("[ ]{2,}", " ", normalized)
    normalized = normalized.strip()

    return normalized

def load_vocab():
    vocab = "PE abcdefghijklmnopqrstuvwxyz'.?"  # P: Padding E: End of Sentence
    char2idx = {char: idx for idx, char in enumerate(vocab)}
    idx2char = {idx: char for idx, char in enumerate(vocab)}
    return char2idx, idx2char

def load_data(training=True):
    # Load vocabulary
    char2idx, idx2char = load_vocab()

    # Parse
    texts, mels, dones, mags = [], [], [], []
    num_samples = 1
    if hp.data == 'deepvoice3-master\BO_chunks':
        metadata = os.path.join(hp.data, 'meta_data.csv')
        for line in codecs.open(metadata, 'r', 'utf-8'):
            fname, _, sent = line.strip().split("|")
            sent = text_normalize(sent) + "E" # text normalization, E: EOS
            if len(sent) <= hp.Tx:
                texts.append(np.array([char2idx[char] for char in sent], np.int32).tostring())
                mels.append(os.path.join(hp.data, "mels", fname + ".npy"))
                dones.append(os.path.join(hp.data, "dones", fname + ".npy"))
                mags.append(os.path.join(hp.data, "mags", fname + ".npy"))

                if num_samples==hp.batch_size:
                    if training: texts, mels, dones, mags = [], [], [], []
                    else: # for evaluation
                        num_samples += 1
                        return texts, mels, dones,  
                num_samples += 1
    # else: # nick
    #     metadata = os.path.join(hp.data, 'metadata.tsv')
    #     for line in codecs.open(metadata, 'r', 'utf-8'):
    #         fname, sent = line.strip().split("\t")
    #         sent = text_normalize(sent) + "E"  # text normalization, E: EOS
    #         if len(sent) <= hp.Tx:
    #             texts.append(np.array([char2idx[char] for char in sent], np.int32).tostring())
    #             mels.append(os.path.join(hp.data, "mels", fname.split("/")[-1].replace(".wav", ".npy")))
    #             dones.append(os.path.join(hp.data, "dones", fname.split("/")[-1].replace(".wav", ".npy")))
    #             mags.append(os.path.join(hp.data, "mags", fname.split("/")[-1].replace(".wav", ".npy")))
    #
    #             if num_samples==hp.batch_size:
    #                 if training: texts, mels, dones, mags = [], [], [], []
    #                 else: # for evaluation
    #                     num_samples += 1
    #                     return texts, mels, dones, mags
    #             num_samples += 1
    return texts, mels, dones, mags

def load_test_data():
    # Load vocabulary
    char2idx, idx2char = load_vocab()

    # Parse
    texts = []
    for line in codecs.open(r'C:\Users\SS Studios\Desktop\SER-based-antispoofing-main\Surya Analysis\deepvoice3-master\test_sents.txt', 'r', 'utf-8'):
        sent = text_normalize(line).strip() + "E" # text normalization, E: EOS
        if len(sent) <= hp.Tx:
            sent += "P"*(hp.Tx-len(sent))
            texts.append([char2idx[char] for char in sent])
    texts = np.array(texts, np.int32)
    return texts

def get_batch():
    """Loads training data and put them in queues"""
    with tf.device('/cpu:0'):
        # Load data
        _texts, _mels, _dones, _mags = load_data()

        # Calc total batch count
        num_batch = len(_texts) // hp.batch_size
         
        # Convert to string tensor
        texts = tf.convert_to_tensor(_texts)
        mels = tf.convert_to_tensor(_mels)
        dones = tf.convert_to_tensor(_dones)
        mags = tf.convert_to_tensor(_mags)
         
        # Create Queues
        text, mel, done, mag = tf.compat.v1.train.slice_input_producer([texts, mels, dones, mags], shuffle=True)

        # Decoding
        text = tf.io.decode_raw(text, tf.int32) # (None,)
        mel = tf.numpy_function(lambda x:np.load(x), [mel], tf.float32) # (None, n_mels)
        done = tf.numpy_function(lambda x:np.load(x), [done], tf.int32) # (None,)
        mag = tf.numpy_function(lambda x:np.load(x), [mag], tf.float32) # (None, 1+n_fft/2)

        # Padding
        text = tf.pad(text, ((0, hp.Tx),))[:hp.Tx] # (Tx,)
        mel = tf.pad(mel, ((0, hp.Ty), (0, 0)))[:hp.Ty] # (Ty, n_mels)
        done = tf.pad(done, ((0, hp.Ty),))[:hp.Ty] # (Ty,)
        mag = tf.pad(mag, ((0, hp.Ty), (0, 0)))[:hp.Ty] # (Ty, 1+n_fft/2)

        # Reduction
        mel = tf.reshape(mel, (hp.Ty//hp.r, -1)) # (Ty/r, n_mels*r)
        done = done[::hp.r] # (Ty/r,)

        # create batch queues
        texts, mels, dones, mags = tf.train.batch([text, mel, done, mag],
                                shapes=[(hp.Tx,), (hp.Ty//hp.r, hp.n_mels*hp.r), (hp.Ty//hp.r,), (hp.Ty, 1+hp.n_fft//2)],
                                num_threads=32,
                                batch_size=hp.batch_size, 
                                capacity=hp.batch_size*32,   
                                dynamic_pad=False)

    return texts, mels, dones, mags, num_batch