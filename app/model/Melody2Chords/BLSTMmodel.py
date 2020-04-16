# -*- coding: utf-8 -*-

import os, sys
import glob
import numpy as np
import pretty_midi
import math

import tensorflow as tf
from keras.models import Sequential
from keras.layers.core import Dense, Activation, RepeatVector, Dropout
from keras.layers.recurrent import LSTM
from keras.layers.wrappers import TimeDistributed, Bidirectional
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, CSVLogger
from keras.models import model_from_json


def make_model(path_json, path_saved_weights):
    # モデル構築
    json_string = open(path_json).read()
    model = model_from_json(json_string)

    model.compile(loss='categorical_crossentropy',
              optimizer=Adam(lr=0.001, beta_1=0.9, beta_2=0.999),
              metrics=['accuracy'])
    model.summary()
    model.load_weights(path_saved_weights)

    return model

notes_li = ['C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5']
chords_li = [['C4', 'E4', 'G4'],
             ['C#4', 'F4', 'G#4'],
             ['D4', 'F#4', 'A4'],
             ['D#4', 'G4', 'A#4'],
             ['E4', 'G#4', 'B4'],
             ['F4', 'A4', 'C4'],
             ['F#4', 'A#4', 'C#4'],
             ['G4', 'B4', 'D4'],
             ['G#4', 'C4', 'D#4'],
             ['A4', 'C#4', 'E4'],
             ['A#4', 'D4', 'F4'],
             ['B4', 'D#4', 'F#4'],

             ['C4', 'D#4', 'G4'],
             ['C#4', 'C4', 'G#4'],
             ['D4', 'F4', 'A4'],
             ['D#4', 'F#4', 'A#4'],
             ['E4', 'G4', 'B4'],
             ['F4', 'G#4', 'C4'],
             ['F#4', 'A4', 'C#4'],
             ['G4', 'A#4', 'D4'],
             ['G#4', 'B4', 'D#4'],
             ['A4', 'C4', 'E4'],
             ['A#4', 'C#4', 'F4'],
             ['B4', 'D4', 'F#4'],
             ]

def make_x_test(dict_note, x_num, y_num):
    x_test = np.zeros((1, 4, 12)) # 4和音からなる1つの和音進行を生成

    for y in range(y_num):
        for x in range(x_num):
            x_test[0, y, notes_li.index(dict_note[str(x)+str(y)][0])] +=  dict_note[str(x)+str(y)][1]

    return x_test

def predict(model, x_test):
    pred = model.predict(x_test)
    pred_argmax = np.argmax(pred, axis=2)
    #print(pred_argmax)

    return pred_argmax

def make_midi(dict_note, pred_argmax, x_num, y_num, TEMPO, NUMERATOR, DENOMINATOR, path_output_melody_chords_midi):

    def calc_notetime(tempo, numerator, denominator):
        notetime = [0] * 10
        j = 64
        for i in range(9):
            notetime[i+1] = 60*numerator*(1/j)/tempo
            j /= 2
        return notetime

    # 音を鳴らす間隔(nt[5]は4分音符)
    nt = calc_notetime(TEMPO, NUMERATOR, DENOMINATOR)

    pm = pretty_midi.PrettyMIDI(resolution=960, initial_tempo=TEMPO)
    instrument = pretty_midi.Instrument(program=89, is_drum=False) # 89:synth pad(fantasia)

    # melody
    time = 0
    for i in range(x_num):
        for j in range(y_num):
            note_name = dict_note[str(i)+str(j)][0]
            note_number = pretty_midi.note_name_to_number(note_name)
            d_time = nt[int(math.log2(64 * dict_note[str(i)+str(j)][1]))]
            # if dict_note[str(i)+str(j)][1] =0.5,
            # d_time = nt[5]

            note = pretty_midi.Note(velocity=100, pitch=note_number, start=time, end=time+d_time)
            instrument.notes.append(note)
            time = time + d_time

    # chords
    time = 0
    for chord_num in pred_argmax[0]:
        note_names = chords_li[chord_num]
        
        d_time = nt[7] # 全音符

        for note_name in note_names:
            note_number = pretty_midi.note_name_to_number(note_name)
            note = pretty_midi.Note(velocity=100, pitch=note_number, start=time, end=time+d_time)
            instrument.notes.append(note)

        time = time + d_time

    pm.instruments.append(instrument)
    pm.write(path_output_melody_chords_midi)

    print('')
    print('FInish generating MIDI file (melody+chord) .')
