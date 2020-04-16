"""
画像を複数のブロックに分割し、
ブロックごとにHSVのVの値の"平均値"を単音に変換して白鍵のみのメロディを生成
1ブロックから1音のみ生成
"""

# -*- coding: utf-8 -*-
from app.model.Image2melody import Image2melody_func as Ifunc
import os, sys

def model(filepath):

    """ 定数管理 """
    ORG_FILE_NAME = filepath # 元画像のパス
    x_num = 4 # 画像をx軸方向に分割する個数
    y_num = 4 # 画像をy軸方向に分割する個数

    TEMPO = 100.0 # テンポ
    NUMERATOR = 4 # 拍子の分子
    DENOMINATOR = 4 # 拍子の分母
    path_output_melody_midi = os.path.join(os.path.dirname(__file__), '../', 'output_midi', 'melody.mid') # 生成されるmidiファイル名


    """ 関数 """
    Ifunc.Info(ORG_FILE_NAME)
    # 画像のサイズ、RGB値、HSV値を表示

    list_note = Ifunc.EdgeDetection(ORG_FILE_NAME, x_num, y_num)
    # 元画像を分割し、それぞれについてHSVのVの値とedgeの量を取得しリストに格納
    # x_num, y_num ... XY座標それぞれにおいて画像を切り取る数
    # list_note ... {'ij' : {'ij' : [ v(HSV), edge ]}

    dict_note = Ifunc.GenDict(list_note)
    # リストからnoteのピッチと長さを取得し辞書に格納

    Ifunc.MelodyAnchoring(dict_note)
    # 各音を並べる順を決定

    Ifunc.GenMIDI(dict_note, x_num, y_num, TEMPO, NUMERATOR, DENOMINATOR, path_output_melody_midi)

    return dict_note
