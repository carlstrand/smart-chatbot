# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief:

import os

import gensim

import config
from domain.util import dump_pkl, load_pkl, segment, segment_pos


def _load_corpus(data_path=None, emb_model_path=None, vec_model=None):
    corpus = dict()
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts and len(parts) > 1:
                q, a = parts[0], parts[1]
                corpus[q] = {'answer': a, 'question_segment': segment(q), 'answer_segment': segment(a),
                             'question_segment_pos': segment_pos(q), 'answer_segment_pos': segment_pos(a)}
    if emb_model_path and vec_model:
        corpus = _add_embedding(emb_model_path, corpus, vec_model)
    return corpus


def _add_embedding(emb_model_path, corpus, vec_model):
    if not os.path.exists(emb_model_path) or not vec_model:
        return corpus, None
    for v in corpus.values():
        v['question_vector'] = [q_word for q_word in v['question_segment'] if q_word in vec_model.index2word]
    return corpus


def load_corpus_model(train_model_path=None, emb_model_path=None, train_data_path=None):
    if not os.path.exists(emb_model_path):
        train_data = _load_corpus(train_data_path)
        sentences = [v['question_segment'] + v['answer_segment'] for v in train_data.values()]
        w2v = gensim.models.Word2Vec(sg=1, sentences=sentences,
                                     size=256, window=5, min_count=config.min_count,
                                     workers=config.num_workers, iter=40)
        # save w2v model
        w2v.wv.save_word2vec_format(emb_model_path, binary=False)
    vec_model = gensim.models.KeyedVectors.load_word2vec_format(emb_model_path, binary=False)
    if os.path.exists(train_model_path):
        corpus = load_pkl(train_model_path)
    elif os.path.exists(train_data_path):
        corpus = _load_corpus(train_data_path, emb_model_path, vec_model)
        # save train model
        dump_pkl(corpus, train_model_path)
    return corpus, vec_model


if __name__ == '__main__':
    load_corpus_model(train_model_path=config.train_model_path,
                      emb_model_path=config.emb_model_path,
                      train_data_path=config.train_file_path)
