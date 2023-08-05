# -*- coding: utf-8 -*-

""" Sequence-to-sequence classifier with the sklearn-like interface

Base module for the sequence-to-sequence classifier, which converts one language sequence into another.
Developing of this module was inspired by this tutorial:

A ten-minute introduction to sequence-to-sequence learning in Keras
Francois Chollet
https://blog.keras.io/a-ten-minute-introduction-to-sequence-to-sequence-learning-in-keras.html

My goal is creating a simple Python package with the sklearn-like interface for solution of different seq2seq tasks
(machine translation, question answering, decoding phonemes sequence into the word sequence, etc.).

Copyright (c) 2018 Ivan Bondarenko <bond005@yandex.ru>

License: Apache License 2.0.

"""

import copy
import os
import tempfile

import keras.backend as K
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import Model
from keras.layers import Input, LSTM, Dense
from keras.optimizers import RMSprop
from keras.utils import Sequence
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_is_fitted


class Seq2SeqLSTM(BaseEstimator, ClassifierMixin):
    """ Sequence-to-sequence classifier, which converts one language sequence into another. """
    def __init__(self, batch_size=64, epochs=100, latent_dim=256, validation_split=0.2, grad_clipping=100.0, lr=0.001,
                 rho=0.9, epsilon=K.epsilon(), lowercase=True, verbose=False):
        """ Create a new object with specified parameters.

        :param batch_size: maximal number of texts or text pairs in the single mini-batch (positive integer).
        :param epochs: maximal number of training epochs (positive integer).
        :param latent_dim: number of units in the LSTM layer (positive integer).
        :param validation_split: the ratio of the evaluation set size to the total number of samples (float between 0
        and 1).
        :param grad_clipping: maximally permissible gradient norm (positive float).
        :param lr: learning rate (positive float)
        :param rho: parameter of the RMSprop algorithm (non-negative float).
        :param epsilon: fuzzy factor.
        :param lowercase: need to bring all tokens of all texts to the lowercase.
        :param verbose: need to printing a training log.

        """
        self.batch_size = batch_size
        self.epochs = epochs
        self.latent_dim = latent_dim
        self.validation_split = validation_split
        self.grad_clipping = grad_clipping
        self.lr = lr
        self.rho = rho
        self.epsilon = epsilon
        self.lowercase = lowercase
        self.verbose = verbose

    def fit(self, X, y, **kwargs):
        """ Fit the seq2seq model to convert sequences one to another.

        Each sequence is unicode text composed from the tokens. Tokens are separated by spaces.

        The RMSprop algorithm is used for training. To avoid overfitting, you must use an early stopping criterion.
        This criterion is included automatically if evaluation set is defined. You can do this in one of two ways:

        1) set a `validation_split` parameter of this object, and in this case evaluation set will be selected as a
        corresponded part of training set proportionally to the `validation_split` value;

        2) set an `eval_set` argument of this method, and then evaluation set is defined entirely by this argument.

        :param X: input texts for training.
        :param y: target texts for training.
        :param eval_set: optional argument containing input and target texts for evaluation during an early-stopping.

        :return self

        """
        self.check_params(**self.get_params(deep=False))
        self.check_X(X, u'X')
        self.check_X(y, u'y')
        if len(X) != len(y):
            raise ValueError(u'`X` does not correspond to `y`! {0} != {1}.'.format(len(X), len(y)))
        if 'eval_set' in kwargs:
            if (not isinstance(kwargs['eval_set'], tuple)) and (not isinstance(kwargs['eval_set'], list)):
                raise ValueError(u'`eval_set` must be `{0}` or `{1}`, not `{2}`!'.format(
                    type((1, 2)), type([1, 2]), type(kwargs['eval_set'])))
            if len(kwargs['eval_set']) != 2:
                raise ValueError(u'`eval_set` must be a two-element sequence! {0} != 2'.format(
                    len(kwargs['eval_set'])))
            self.check_X(kwargs['eval_set'][0], u'X_eval_set')
            self.check_X(kwargs['eval_set'][1], u'y_eval_set')
            if len(kwargs['eval_set'][0]) != len(kwargs['eval_set'][1]):
                raise ValueError(u'`X_eval_set` does not correspond to `y_eval_set`! {0} != {1}.'.format(
                    len(kwargs['eval_set'][0]), len(kwargs['eval_set'][1])))
            X_eval_set = kwargs['eval_set'][0]
            y_eval_set = kwargs['eval_set'][1]
        else:
            if self.validation_split is None:
                X_eval_set = None
                y_eval_set = None
            else:
                n_eval_set = int(round(len(X) * self.validation_split))
                if n_eval_set < 1:
                    raise ValueError(u'`validation_split` is too small! There are no samples for evaluation!')
                if n_eval_set >= len(X):
                    raise ValueError(u'`validation_split` is too large! There are no samples for training!')
                X_eval_set = X[-n_eval_set:-1]
                y_eval_set = y[-n_eval_set:-1]
                X = X[:-n_eval_set]
                y = y[:-n_eval_set]
        input_characters = set()
        target_characters = set()
        max_encoder_seq_length = 0
        max_decoder_seq_length = 0
        for sample_ind in range(len(X)):
            prep = self.tokenize_text(X[sample_ind], self.lowercase)
            n = len(prep)
            if n == 0:
                raise ValueError(u'Sample {0} of `X` is wrong! This sample is empty.'.format(sample_ind))
            if n > max_encoder_seq_length:
                max_encoder_seq_length = n
            input_characters |= set(prep)
            prep = self.tokenize_text(y[sample_ind], self.lowercase)
            n = len(prep)
            if n == 0:
                raise ValueError(u'Sample {0} of `y` is wrong! This sample is empty.'.format(sample_ind))
            if (n + 2) > max_decoder_seq_length:
                max_decoder_seq_length = n + 2
            target_characters |= set(prep)
        if len(input_characters) == 0:
            raise ValueError(u'`X` is empty!')
        if len(target_characters) == 0:
            raise ValueError(u'`y` is empty!')
        input_characters_ = set()
        target_characters_ = set()
        if (X_eval_set is not None) and (y_eval_set is not None):
            for sample_ind in range(len(X_eval_set)):
                prep = self.tokenize_text(X_eval_set[sample_ind], self.lowercase)
                n = len(prep)
                if n == 0:
                    raise ValueError(u'Sample {0} of `X_eval_set` is wrong! This sample is empty.'.format(sample_ind))
                if n > max_encoder_seq_length:
                    max_encoder_seq_length = n
                input_characters_ |= set(prep)
                prep = self.tokenize_text(y_eval_set[sample_ind], self.lowercase)
                n = len(prep)
                if n == 0:
                    raise ValueError(u'Sample {0} of `y_eval_set` is wrong! This sample is empty.'.format(sample_ind))
                if (n + 2) > max_decoder_seq_length:
                    max_decoder_seq_length = n + 2
                target_characters_ |= set(prep)
            if len(input_characters_) == 0:
                raise ValueError(u'`X_eval_set` is empty!')
            if len(target_characters_) == 0:
                raise ValueError(u'`y_eval_set` is empty!')
        input_characters = sorted(list(input_characters | input_characters_))
        target_characters = sorted(list(target_characters | target_characters_ | {u'\t', u'\n'}))
        if self.verbose:
            print(u'')
            print(u'Number of samples for training:', len(X))
            if X_eval_set is not None:
                print(u'Number of samples for evaluation and early stopping:', len(X_eval_set))
            print(u'Number of unique input tokens:', len(input_characters))
            print(u'Number of unique output tokens:', len(target_characters))
            print(u'Max sequence length for inputs:', max_encoder_seq_length)
            print(u'Max sequence length for outputs:', max_decoder_seq_length)
            print(u'')
        self.input_token_index_ = dict([(char, i) for i, char in enumerate(input_characters)])
        self.target_token_index_ = dict([(char, i) for i, char in enumerate(target_characters)])
        self.max_encoder_seq_length_ = max_encoder_seq_length
        self.max_decoder_seq_length_ = max_decoder_seq_length
        encoder_inputs = Input(shape=(None, len(self.input_token_index_)))
        encoder = LSTM(self.latent_dim, return_sequences=False, return_state=True)
        encoder_outputs, state_h, state_c = encoder(encoder_inputs)
        encoder_states = [state_h, state_c]
        decoder_inputs = Input(shape=(None, len(self.target_token_index_)))
        decoder_lstm = LSTM(self.latent_dim, return_sequences=True, return_state=True)
        decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
        decoder_dense = Dense(len(self.target_token_index_), activation='softmax')
        decoder_outputs = decoder_dense(decoder_outputs)
        model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
        optimizer = RMSprop(lr=self.lr, rho=self.rho, epsilon=self.epsilon, decay=0.0, clipnorm=self.grad_clipping)
        model.compile(optimizer=optimizer, loss='categorical_crossentropy')
        training_set_generator = TextPairSequence(
            input_texts=X, target_texts=y,
            batch_size=self.batch_size,
            max_encoder_seq_length=max_encoder_seq_length, max_decoder_seq_length=max_decoder_seq_length,
            input_token_index=self.input_token_index_, target_token_index=self.target_token_index_,
            lowercase=self.lowercase
        )
        if (X_eval_set is not None) and (y_eval_set is not None):
            evaluation_set_generator = TextPairSequence(
                input_texts=X_eval_set, target_texts=y_eval_set,
                batch_size=self.batch_size,
                max_encoder_seq_length=max_encoder_seq_length, max_decoder_seq_length=max_decoder_seq_length,
                input_token_index=self.input_token_index_, target_token_index=self.target_token_index_,
                lowercase=self.lowercase
            )
            callbacks = [
                EarlyStopping(patience=5, verbose=(1 if self.verbose else 0))
            ]
        else:
            evaluation_set_generator = None
            callbacks = []
        tmp_weights_name = self.get_temp_name()
        try:
            callbacks.append(
                ModelCheckpoint(filepath=tmp_weights_name, verbose=(1 if self.verbose else 0), save_best_only=True,
                                save_weights_only=True)
            )
            model.fit_generator(
                generator=training_set_generator,
                epochs=self.epochs, verbose=(1 if self.verbose else 0),
                shuffle=True,
                validation_data=evaluation_set_generator,
                callbacks=callbacks
            )
            if os.path.isfile(tmp_weights_name):
                model.load_weights(tmp_weights_name)
        finally:
            if os.path.isfile(tmp_weights_name):
                os.remove(tmp_weights_name)
        self.encoder_model_ = Model(encoder_inputs, encoder_states)
        decoder_state_input_h = Input(shape=(self.latent_dim,))
        decoder_state_input_c = Input(shape=(self.latent_dim,))
        decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
        decoder_outputs, state_h, state_c = decoder_lstm(
            decoder_inputs, initial_state=decoder_states_inputs)
        decoder_states = [state_h, state_c]
        decoder_outputs = decoder_dense(decoder_outputs)
        self.decoder_model_ = Model(
            [decoder_inputs] + decoder_states_inputs,
            [decoder_outputs] + decoder_states)
        self.reverse_target_char_index_ = dict(
            (i, char) for char, i in self.target_token_index_.items())
        return self

    def predict(self, X):
        """ Predict resulting sequences of tokens by source sequences with a trained seq2seq model.

        Each sequence is unicode text composed from the tokens. Tokens are separated by spaces.

        :param X: source sequences.

        :return: resulting sequences, predicted for source sequences.

        """
        self.check_X(X, u'X')
        check_is_fitted(self, ['input_token_index_', 'target_token_index_', 'reverse_target_char_index_',
                               'max_encoder_seq_length_', 'max_decoder_seq_length_',
                               'encoder_model_', 'decoder_model_'])
        texts = list()
        for input_seq in Seq2SeqLSTM.generate_data_for_prediction(
                input_texts=X, batch_size=self.batch_size, max_encoder_seq_length=self.max_encoder_seq_length_,
                input_token_index=self.input_token_index_, lowercase=self.lowercase
        ):
            batch_size = input_seq.shape[0]
            states_value = self.encoder_model_.predict(input_seq)
            target_seq = np.zeros((batch_size, 1, len(self.target_token_index_)), dtype=np.float32)
            stop_conditions = []
            decoded_sentences = []
            for text_idx in range(batch_size):
                target_seq[text_idx, 0, self.target_token_index_[u'\t']] = 1.0
                stop_conditions.append(False)
                decoded_sentences.append([])
            while not all(stop_conditions):
                output_tokens, h, c = self.decoder_model_.predict([target_seq] + states_value)
                indices_of_sampled_tokens = np.argmax(output_tokens[:, -1, :], axis=1)
                for text_idx in range(batch_size):
                    if stop_conditions[text_idx]:
                        continue
                    sampled_char = self.reverse_target_char_index_[indices_of_sampled_tokens[text_idx]]
                    decoded_sentences[text_idx].append(sampled_char)
                    if (sampled_char == u'\n') or (len(decoded_sentences[text_idx]) > self.max_decoder_seq_length_):
                        stop_conditions[text_idx] = True
                    for token_idx in range(len(self.target_token_index_)):
                        target_seq[text_idx][0][token_idx] = 0.0
                    target_seq[text_idx, 0, indices_of_sampled_tokens[text_idx]] = 1.0
                states_value = [h, c]
            for text_idx in range(batch_size):
                texts.append(u' '.join(decoded_sentences[text_idx]))
            del input_seq
        if isinstance(X, tuple):
            return tuple(texts)
        if isinstance(X, np.ndarray):
            return np.array(texts, dtype=object)
        return texts

    def fit_predict(self, X, y, **kwargs):
        return self.fit(X, y, **kwargs).predict(X)

    def load_weights(self, weights_as_bytes):
        """ Load weights of neural model from the binary data.

        :param weights_as_bytes: 2-element tuple of binary data (`bytes` or `byterray` objects) containing weights of
        neural encoder and neural decoder respectively.
        """
        if not isinstance(weights_as_bytes, tuple):
            raise ValueError(u'`weights_as_bytes` must be a 2-element tuple, not `{0}`!'.format(type(weights_as_bytes)))
        if len(weights_as_bytes) != 2:
            raise ValueError(u'`weights_as_bytes` must be a 2-element tuple, but it is a {0}-element tuple!'.format(
                len(weights_as_bytes)))
        if (not isinstance(weights_as_bytes[0], bytearray)) and (not isinstance(weights_as_bytes[0], bytes)):
            raise ValueError(u'First element of `weights_as_bytes` must be an array of bytes, not `{0}`!'.format(
                type(weights_as_bytes[0])))
        if (not isinstance(weights_as_bytes[1], bytearray)) and (not isinstance(weights_as_bytes[1], bytes)):
            raise ValueError(u'Second element of `weights_as_bytes` must be an array of bytes, not `{0}`!'.format(
                type(weights_as_bytes[1])))
        tmp_weights_name = self.get_temp_name()
        try:
            encoder_inputs = Input(shape=(None, len(self.input_token_index_)))
            encoder = LSTM(self.latent_dim, return_sequences=False, return_state=True)
            encoder_outputs, state_h, state_c = encoder(encoder_inputs)
            encoder_states = [state_h, state_c]
            decoder_inputs = Input(shape=(None, len(self.target_token_index_)))
            decoder_lstm = LSTM(self.latent_dim, return_sequences=True, return_state=True)
            decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
            decoder_dense = Dense(len(self.target_token_index_), activation='softmax')
            self.encoder_model_ = Model(encoder_inputs, encoder_states)
            decoder_state_input_h = Input(shape=(self.latent_dim,))
            decoder_state_input_c = Input(shape=(self.latent_dim,))
            decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
            decoder_outputs, state_h, state_c = decoder_lstm(
                decoder_inputs, initial_state=decoder_states_inputs)
            decoder_states = [state_h, state_c]
            decoder_outputs = decoder_dense(decoder_outputs)
            self.decoder_model_ = Model(
                [decoder_inputs] + decoder_states_inputs,
                [decoder_outputs] + decoder_states)
            with open(tmp_weights_name, 'wb') as fp:
                fp.write(weights_as_bytes[0])
            self.encoder_model_.load_weights(tmp_weights_name)
            os.remove(tmp_weights_name)
            with open(tmp_weights_name, 'wb') as fp:
                fp.write(weights_as_bytes[1])
            self.decoder_model_.load_weights(tmp_weights_name)
            os.remove(tmp_weights_name)
        finally:
            if os.path.isfile(tmp_weights_name):
                os.remove(tmp_weights_name)

    def dump_weights(self):
        """ Dump weights of neural model as binary data.

        :return: 2-element tuple of binary data (`bytes` objects) containing weights of neural encoder and
        neural decoder respectively.
        """
        check_is_fitted(self, ['input_token_index_', 'target_token_index_', 'reverse_target_char_index_',
                               'max_encoder_seq_length_', 'max_decoder_seq_length_',
                               'encoder_model_', 'decoder_model_'])
        tmp_weights_name = self.get_temp_name()
        try:
            if os.path.isfile(tmp_weights_name):
                os.remove(tmp_weights_name)
            self.encoder_model_.save_weights(tmp_weights_name)
            with open(tmp_weights_name, 'rb') as fp:
                weights_of_encoder = fp.read()
            os.remove(tmp_weights_name)
            self.decoder_model_.save_weights(tmp_weights_name)
            with open(tmp_weights_name, 'rb') as fp:
                weights_of_decoder = fp.read()
            os.remove(tmp_weights_name)
            weights_as_bytearray = (weights_of_encoder, weights_of_decoder)
        finally:
            if os.path.isfile(tmp_weights_name):
                os.remove(tmp_weights_name)
        return weights_as_bytearray

    def get_params(self, deep=True):
        """ Get parameters for this estimator.

        This method is necessary for using the `Seq2SeqLSTM` object in such scikit-learn classes as `Pipeline` etc.

        :param deep: If True, will return the parameters for this estimator and contained subobjects that are estimators

        :return Parameter names mapped to their values.

        """
        return {'batch_size': self.batch_size, 'epochs': self.epochs, 'latent_dim': self.latent_dim,
                'validation_split': self.validation_split, 'lr': self.lr, 'rho': self.rho, 'epsilon': self.epsilon,
                'lowercase': self.lowercase, 'verbose': self.verbose, 'grad_clipping': self.grad_clipping}

    def set_params(self, **params):
        """ Set parameters for this estimator.

        This method is necessary for using the `Seq2SeqLSTM` object in such scikit-learn classes as `Pipeline` etc.

        :param params: dictionary with new values of parameters for the seq2seq estimator.

        :return self.

        """
        for parameter, value in params.items():
            self.__setattr__(parameter, value)
        return self

    def dump_all(self):
        """ Dump all data of the neural model.

        This method is used in the serialization and copying of object.

        :return: dictionary with names and saved values of all parameters, specified in the constructor and received as
        result of training.
        """
        try:
            check_is_fitted(self, ['input_token_index_', 'target_token_index_', 'reverse_target_char_index_',
                                   'max_encoder_seq_length_', 'max_decoder_seq_length_',
                                   'encoder_model_', 'decoder_model_'])
            is_trained = True
        except:
            is_trained = False
        params = self.get_params(True)
        if is_trained:
            params['weights'] = self.dump_weights()
            params['input_token_index_'] = copy.deepcopy(self.input_token_index_)
            params['target_token_index_'] = copy.deepcopy(self.target_token_index_)
            params['reverse_target_char_index_'] = copy.deepcopy(self.reverse_target_char_index_)
            params['max_encoder_seq_length_'] = self.max_encoder_seq_length_
            params['max_decoder_seq_length_'] = self.max_decoder_seq_length_
        return params

    def load_all(self, new_params):
        """ Load all data of the neural model.

        This method is used in the deserialization and copying of object.

        :param new_params: dictionary with names and new values of all parameters, specified in the constructor and
        received as result of training.

        :return: self.
        """
        if not isinstance(new_params, dict):
            raise ValueError(u'`new_params` is wrong! Expected {0}.'.format(type({0: 1})))
        self.check_params(**new_params)
        expected_param_keys = {'batch_size', 'epochs', 'latent_dim', 'validation_split', 'lr', 'rho',
                               'epsilon', 'lowercase', 'verbose', 'grad_clipping'}
        params_after_training = {'weights', 'input_token_index_', 'target_token_index_', 'reverse_target_char_index_',
                                 'max_encoder_seq_length_', 'max_decoder_seq_length_'}
        is_fitted = len(set(new_params.keys())) > len(expected_param_keys)
        if is_fitted:
            if set(new_params.keys()) != (expected_param_keys | params_after_training):
                raise ValueError(u'`new_params` does not contain all expected keys!')
        self.batch_size = new_params['batch_size']
        self.epochs = new_params['epochs']
        self.latent_dim = new_params['latent_dim']
        self.validation_split = new_params['validation_split']
        self.lr = new_params['lr']
        self.rho = new_params['rho']
        self.epsilon = new_params['epsilon']
        self.lowercase = new_params['lowercase']
        self.verbose = new_params['verbose']
        self.grad_clipping = new_params['grad_clipping']
        if is_fitted:
            if not isinstance(new_params['input_token_index_'], dict):
                raise ValueError(u'`new_params` is wrong! `input_token_index_` must be the `{0}`!'.format(
                    type({1: 'a', 2: 'b'})))
            if not isinstance(new_params['target_token_index_'], dict):
                raise ValueError(u'`new_params` is wrong! `target_token_index_` must be the `{0}`!'.format(
                    type({1: 'a', 2: 'b'})))
            if not isinstance(new_params['reverse_target_char_index_'], dict):
                raise ValueError(u'`new_params` is wrong! `reverse_target_char_index_` must be the `{0}`!'.format(
                    type({1: 'a', 2: 'b'})))
            if not isinstance(new_params['max_encoder_seq_length_'], int):
                raise ValueError(u'`new_params` is wrong! `max_encoder_seq_length_` must be the `{0}`!'.format(
                    type(10)))
            if new_params['max_encoder_seq_length_'] < 1:
                raise ValueError(u'`new_params` is wrong! `max_encoder_seq_length_` must be a positive integer number!')
            if not isinstance(new_params['max_decoder_seq_length_'], int):
                raise ValueError(u'`new_params` is wrong! `max_decoder_seq_length_` must be the `{0}`!'.format(
                    type(10)))
            if new_params['max_decoder_seq_length_'] < 1:
                raise ValueError(u'`new_params` is wrong! `max_decoder_seq_length_` must be a positive integer number!')
            self.max_decoder_seq_length_ = new_params['max_decoder_seq_length_']
            self.max_encoder_seq_length_ = new_params['max_encoder_seq_length_']
            self.input_token_index_ = copy.deepcopy(new_params['input_token_index_'])
            self.target_token_index_ = copy.deepcopy(new_params['target_token_index_'])
            self.reverse_target_char_index_ = copy.deepcopy(new_params['reverse_target_char_index_'])
            self.load_weights(new_params['weights'])
        return self

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.load_all(self.dump_all())
        return result

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        result.load_all(self.dump_all())
        return result

    def __getstate__(self):
        """ Serialize this object into the specified state.

        :return serialized state as Python dictionary.

        """
        return self.dump_all()

    def __setstate__(self, state):
        """ Deserialize this object from the specified state.

        :param state: serialized state as Python dictionary.

        """
        self.load_all(state)

    @staticmethod
    def check_params(**kwargs):
        """ Check values of all parameters and raise `ValueError` if incorrect values are found.

        :param kwargs: dictionary containing names and values of all parameters.

        """
        if 'batch_size' not in kwargs:
            raise ValueError(u'`batch_size` is not found!')
        if not isinstance(kwargs['batch_size'], int):
            raise ValueError(u'`batch_size` must be `{0}`, not `{1}`.'.format(type(10), type(kwargs['batch_size'])))
        if kwargs['batch_size'] < 1:
            raise ValueError(u'`batch_size` must be a positive number! {0} is not positive.'.format(
                kwargs['batch_size']))
        if 'epochs' not in kwargs:
            raise ValueError(u'`epochs` is not found!')
        if not isinstance(kwargs['epochs'], int):
            raise ValueError(u'`epochs` must be `{0}`, not `{1}`.'.format(type(10), type(kwargs['epochs'])))
        if kwargs['epochs'] < 1:
            raise ValueError(u'`epochs` must be a positive number! {0} is not positive.'.format(kwargs['epochs']))
        if 'latent_dim' not in kwargs:
            raise ValueError(u'`latent_dim` is not found!')
        if not isinstance(kwargs['latent_dim'], int):
            raise ValueError(u'`latent_dim` must be `{0}`, not `{1}`.'.format(type(10), type(kwargs['latent_dim'])))
        if kwargs['latent_dim'] < 1:
            raise ValueError(u'`latent_dim` must be a positive number! {0} is not positive.'.format(
                kwargs['latent_dim']))
        if 'lowercase' not in kwargs:
            raise ValueError(u'`lowercase` is not found!')
        if (not isinstance(kwargs['lowercase'], int)) and (not isinstance(kwargs['lowercase'], bool)):
            raise ValueError(u'`lowercase` must be `{0}` or `{1}`, not `{2}`.'.format(type(10), type(True),
                                                                                      type(kwargs['lowercase'])))
        if 'verbose' not in kwargs:
            raise ValueError(u'`verbose` is not found!')
        if (not isinstance(kwargs['verbose'], int)) and (not isinstance(kwargs['verbose'], bool)):
            raise ValueError(u'`verbose` must be `{0}` or `{1}`, not `{2}`.'.format(type(10), type(True),
                                                                                    type(kwargs['verbose'])))
        if 'validation_split' not in kwargs:
            raise ValueError(u'`validation_split` is not found!')
        if kwargs['validation_split'] is not None:
            if not isinstance(kwargs['validation_split'], float):
                raise ValueError(u'`validation_split` must be `{0}`, not `{1}`.'.format(
                    type(1.5), type(kwargs['validation_split'])))
            if (kwargs['validation_split'] <= 0.0) or (kwargs['validation_split'] >= 1.0):
                raise ValueError(u'`validation_split` must be in interval (0.0, 1.0)!')
        if 'lr' not in kwargs:
            raise ValueError(u'`lr` is not found!')
        if not isinstance(kwargs['lr'], float):
            raise ValueError(u'`lr` must be `{0}`, not `{1}`.'.format(type(1.5), type(kwargs['lr'])))
        if kwargs['lr'] <= 0.0:
            raise ValueError(u'`lr` must be a positive floating-point value!')
        if 'grad_clipping' not in kwargs:
            raise ValueError(u'`grad_clipping` is not found!')
        if not isinstance(kwargs['grad_clipping'], float):
            raise ValueError(u'`grad_clipping` must be `{0}`, not `{1}`.'.format(type(1.5),
                                                                                 type(kwargs['grad_clipping'])))
        if kwargs['grad_clipping'] <= 0.0:
            raise ValueError(u'`grad_clipping` must be a positive floating-point value!')
        if 'rho' not in kwargs:
            raise ValueError(u'`rho` is not found!')
        if not isinstance(kwargs['rho'], float):
            raise ValueError(u'`rho` must be `{0}`, not `{1}`.'.format(type(1.5), type(kwargs['rho'])))
        if kwargs['rho'] < 0.0:
            raise ValueError(u'`rho` must be a non-negative floating-point value!')
        if 'epsilon' not in kwargs:
            raise ValueError(u'`epsilon` is not found!')
        if not isinstance(kwargs['epsilon'], float):
            raise ValueError(u'`epsilon` must be `{0}`, not `{1}`.'.format(type(1.5), type(kwargs['epsilon'])))
        if kwargs['epsilon'] < 0.0:
            raise ValueError(u'`epsilon` must be a non-negative floating-point value!')

    @staticmethod
    def check_X(X, checked_object_name=u'X'):
        """ Check correctness of specified sequences (texts) and raise `ValueError` if wrong values are found.

        :param X: sequences for checking (list, tuple or numpy.ndarray object, containing the unicode strings).
        :param checked_object_name: printed name of object containing sequences.

        """
        if (not isinstance(X, list)) and (not isinstance(X, tuple)) and (not isinstance(X, np.ndarray)):
            raise ValueError(u'`{0}` is wrong type for `{1}`.'.format(type(X), checked_object_name))
        if isinstance(X, np.ndarray):
            if len(X.shape) != 1:
                raise ValueError(u'`{0}` must be a 1-D array!'.format(checked_object_name))
        n = len(X)
        if n == 0:
            raise ValueError(u'{0} is empty!'.format(checked_object_name))
        for sample_ind in range(n):
            if not hasattr(X[sample_ind], 'split'):
                raise ValueError(u'Sample {0} of `{1}` is wrong! This sample have not the `split` method.'.format(
                    sample_ind, checked_object_name))

    @staticmethod
    def tokenize_text(src, lowercase):
        """ Split source text by spaces and bring the resulting tokens to lowercase optionally.

        :param src: source text as unicode string.
        :param lowercase: if True, will bring all tokens to lowercase.

        :return list of tokens as strings.

        """
        return list(filter(lambda it: len(it) > 0, src.strip().lower().split() if lowercase else src.strip().split()))

    @staticmethod
    def get_temp_name():
        """ Get name of temporary file for saving/loading of neural network weights.

        :return name of file as string.

        """
        fp = tempfile.NamedTemporaryFile(delete=True)
        file_name = fp.name
        fp.close()
        del fp
        return file_name

    @staticmethod
    def generate_data_for_prediction(input_texts, batch_size, max_encoder_seq_length, input_token_index, lowercase):
        """ Generate feature matrices based on one-hot vectorization for input texts by mini-batches.

        This generator is used in the prediction process by means of the trained neural model. Each text is a unicode
        string in which all tokens are separated by spaces. It generates a 3-D array (numpy.ndarray object), using
        one-hot enconding (first dimension is index of text in the mini-batch, second dimension is a timestep, or token
        position in this text, and third dimension is index of this token in the input vocabulary).

        :param input_texts: sequence (list, tuple or numpy.ndarray) of input texts.
        :param batch_size: target size of single mini-batch, i.e. number of text pairs in this mini-batch.
        :param max_encoder_seq_length: maximal length of any input text.
        :param input_token_index: the special index for one-hot encoding any input text as numerical feature matrix.
        :param lowercase: the need to bring all tokens of all texts to the lowercase.

        :return the 3-D array representation of input mini-batch data.

        """
        n = len(input_texts)
        n_batches = n // batch_size
        while (n_batches * batch_size) < n:
            n_batches += 1
        start_pos = 0
        for batch_ind in range(n_batches - 1):
            end_pos = start_pos + batch_size
            encoder_input_data = np.zeros((batch_size, max_encoder_seq_length, len(input_token_index)),
                                          dtype=np.float32)
            for i, input_text in enumerate(input_texts[start_pos:end_pos]):
                for t, char in enumerate(Seq2SeqLSTM.tokenize_text(input_text, lowercase)):
                    if t >= max_encoder_seq_length:
                        break
                    encoder_input_data[i, t, input_token_index[char]] = 1.0
            start_pos = end_pos
            yield encoder_input_data
        end_pos = n
        encoder_input_data = np.zeros((end_pos - start_pos, max_encoder_seq_length, len(input_token_index)),
                                      dtype=np.float32)
        for i, input_text in enumerate(input_texts[start_pos:end_pos]):
            for t, char in enumerate(Seq2SeqLSTM.tokenize_text(input_text, lowercase)):
                if t >= max_encoder_seq_length:
                    break
                encoder_input_data[i, t, input_token_index[char]] = 1.0
        yield encoder_input_data


class TextPairSequence(Sequence):
    """ Object for fitting to a sequence of text pairs without calculating features for all these pairs in memory.

    """
    def __init__(self, input_texts, target_texts, batch_size, max_encoder_seq_length, max_decoder_seq_length,
                 input_token_index, target_token_index, lowercase):
        """ Generate feature matrices based on one-hot vectorization for pairs of texts by mini-batches.

        This generator is used in the training process of the neural model (see the `fit_generator` method of the Keras
        `Model` object). Each text (input or target one) is a unicode string in which all tokens are separated by
        spaces. Each pair of texts generates three 3-D arrays (numpy.ndarray objects):

        1) one-hot vectorization of corresponded input text (first dimension is index of text in the mini-batch, second
        dimension is a timestep, or token position in this text, and third dimension is index of this token in the input
        vocabulary);

        2) one-hot vectorization of corresponded target text (first dimension is index of text in the mini-batch, second
        dimension is a timestep, or token position in this text, and third dimension is index of this token in the
        target vocabulary);

        3) array is the same as second one but offset by one timestep.

        In the training process first and second array will be fed into the neural model, and third array will be
        considered as its desired output.

        :param input_texts: sequence (list, tuple or numpy.ndarray) of input texts.
        :param target_texts: sequence (list, tuple or numpy.ndarray) of target texts.
        :param batch_size: target size of single mini-batch, i.e. number of text pairs in this mini-batch.
        :param max_encoder_seq_length: maximal length of any input text.
        :param max_decoder_seq_length: maximal length of any target text.
        :param input_token_index: the special index for one-hot encoding any input text as numerical feature matrix.
        :param target_token_index: the special index for one-hot encoding any target text as numerical feature matrix.
        :param lowercase: the need to bring all tokens of all texts to the lowercase.

        :return the two-element tuple with input and output mini-batch data for the neural model training respectively.

        """
        self.input_texts = input_texts
        self.target_texts = target_texts
        self.batch_size = batch_size
        self.max_encoder_seq_length = max_encoder_seq_length
        self.max_decoder_seq_length = max_decoder_seq_length
        self.input_token_index = input_token_index
        self.target_token_index = target_token_index
        self.lowercase = lowercase
        self.n_text_pairs = len(self.input_texts)
        self.n_batches = self.n_text_pairs // self.batch_size
        while (self.n_batches * self.batch_size) < self.n_text_pairs:
            self.n_batches += 1

    def __len__(self):
        return self.n_batches

    def __getitem__(self, idx):
        start_pos = idx * self.batch_size
        end_pos = start_pos + self.batch_size
        encoder_input_data = np.zeros((self.batch_size, self.max_encoder_seq_length, len(self.input_token_index)),
                                      dtype=np.float32)
        decoder_input_data = np.zeros((self.batch_size, self.max_decoder_seq_length, len(self.target_token_index)),
                                      dtype=np.float32)
        decoder_target_data = np.zeros((self.batch_size, self.max_decoder_seq_length, len(self.target_token_index)),
                                       dtype=np.float32)
        idx_in_batch = 0
        for src_text_idx in range(start_pos, end_pos):
            prep_text_idx = src_text_idx
            while prep_text_idx >= self.n_text_pairs:
                prep_text_idx = prep_text_idx - self.n_text_pairs
            input_text = self.input_texts[prep_text_idx]
            target_text = self.target_texts[prep_text_idx]
            for t, char in enumerate(Seq2SeqLSTM.tokenize_text(input_text, self.lowercase)):
                encoder_input_data[idx_in_batch, t, self.input_token_index[char]] = 1.0
            for t, char in enumerate([u'\t'] + Seq2SeqLSTM.tokenize_text(target_text, self.lowercase) + [u'\n']):
                decoder_input_data[idx_in_batch, t, self.target_token_index[char]] = 1.0
                if t > 0:
                    decoder_target_data[idx_in_batch, t - 1, self.target_token_index[char]] = 1.0
            idx_in_batch += 1
        return [encoder_input_data, decoder_input_data], decoder_target_data
