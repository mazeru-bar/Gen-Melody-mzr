# -*- coding: utf-8 -*-

import os, sys
import numpy as np
from app.model.Melody2Chords import BLSTMmodel as BModel

""" 定数管理 """
path_saved_weights = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weight_h5', 'weights_e300.h5')
path_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_json', 'model.json')
x_num = 4 # 画像をx軸方向に分割する個数
y_num = 4 # 画像をy軸方向に分割する個数

TEMPO = 100.0 # テンポ
NUMERATOR = 4 # 拍子の分子
DENOMINATOR = 4 # 拍子の分母

path_output_melody_chords_midi = os.path.join(os.path.dirname(__file__), '../', 'output_midi', 'melody_chords.mid') # 生成されるmidiファイル名

def model_test(dict_note):
    model = BModel.make_model(path_json=path_json, path_saved_weights=path_saved_weights)
    x_test = BModel.make_x_test(dict_note, x_num, y_num)

    # melodyからchordsの予測
    pred_argmax = BModel.predict(model, x_test)
    # midiファイル(melody+chords)生成
    BModel.make_midi(dict_note, pred_argmax, x_num, y_num, TEMPO, NUMERATOR, DENOMINATOR, path_output_melody_chords_midi)

    return pred_argmax
