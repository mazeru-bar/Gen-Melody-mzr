"""
元画像を複数のブロックに分割し、
　ブロックごとにHSVのVの値の"平均値"を単音に変換して白鍵のみのメロディを生成
1ブロックから1音のみ生成
エッジの多さをどのように音の長さに変換すべきか不明なため一旦note_lengthの値を0.5に固定
"""

# -*- coding: utf-8 -*-
import cv2
import numpy as np
import sys
import pprint
import pretty_midi

def Info(ORG_FILE_NAME):
    org_img = cv2.imread(ORG_FILE_NAME, cv2.IMREAD_UNCHANGED)

    # 画像のサイズを表示
    print('='*10 + ' Info ' + '='*10)
    # カラー
    if len(org_img.shape) == 3:
        height, width, channels = org_img.shape[:3]
    # グレースケール
    else:
        height, width = org_img.shape[:2]
        channels = 1
    print("width: " + str(width))
    print("height: " + str(height))
    print("channels: " + str(channels))
    print("dtype: " + str(org_img.dtype))

    # 対象範囲を切り出し
    boxFromX = 0 #対象範囲開始位置 X座標
    boxFromY = 0 #対象範囲開始位置 Y座標
    boxToX = width//6 #対象範囲終了位置 X座標
    boxToY = height//6 #対象範囲終了位置 Y座標
    # y:y+h, x:x+w　の順で設定
    imgBox = org_img[boxFromY: boxToY, boxFromX: boxToX]

    # RGB平均値を出力
    # flattenで一次元化しmeanで平均を取得
    b = imgBox.T[0].flatten().mean()
    g = imgBox.T[1].flatten().mean()
    r = imgBox.T[2].flatten().mean()

    # RGB平均値を取得
    print('-'*10 + ' RGB ' + '-'*10)
    print("B: %.2f" % (b))
    print("G: %.2f" % (g))
    print("R: %.2f" % (r))

    # BGRからHSVに変換
    imgBoxHsv = cv2.cvtColor(imgBox,cv2.COLOR_BGR2HSV)

    # HSV平均値を取得
    # flattenで一次元化しmeanで平均を取得
    h = imgBoxHsv.T[0].flatten().mean()
    s = imgBoxHsv.T[1].flatten().mean()
    v = imgBoxHsv.T[2].flatten().mean()

    # HSV平均値を出力
    # uHeは[0,179], Saturationは[0,255]，Valueは[0,255]
    print('-'*10 + ' HSV ' + '-'*10)
    print("Hue: %.2f" % (h))
    print("Salute: %.2f" % (s))
    print("Value: %.2f" % (v))

def EdgeDetection(ORG_FILE_NAME, x_num=4, y_num=4):
    # 元の画像を読み込む
    org_img = cv2.imread(ORG_FILE_NAME, cv2.IMREAD_UNCHANGED)
    # グレースケールに変換
    gray_img = cv2.imread(ORG_FILE_NAME, cv2.IMREAD_GRAYSCALE)
    # エッジ抽出
    canny_img = cv2.Canny(gray_img, 100, 200)

    # 画像ファイルの読み込みに失敗したらエラー終了
    if org_img is None:
        print("Failed to load image file.")
        sys.exit(1)

    # カラー
    if len(org_img.shape) == 3:
        height, width, channels = org_img.shape[:3]
    # グレースケール
    else:
        height, width = org_img.shape[:2]
        channels = 1

    list_note = [] # {'ij' : [ v(HSV), edge ]}

    for i in range(x_num):
        for j in range(y_num):

            """ エッジ検出 """
            # 定数定義
            ORGBOX_WINDOW_NAME = 'org'
            GRAYBOX_WINDOW_NAME = 'gray'
            CANNYBOX_WINDOW_NAME = 'canny'

            GRAYBOX_FILE_NAME = 'data/gray/'+str(i)+str(j)+'.jpg'
            CANNYBOX_FILE_NAME = 'data/canny/'+str(i)+str(j)+'.jpg'

            # 対象範囲を切り出し
            boxFromX = i*(width//x_num) #対象範囲開始位置 X座標
            boxFromY = j*(height//y_num) #対象範囲開始位置 Y座標
            boxToX = (i+1)*(width//x_num) #対象範囲終了位置 X座標
            boxToY = (j+1)*(height//y_num) #対象範囲終了位置 Y座標
            #print(boxFromX,boxToX,boxFromX,boxFromY)

            # y:y+h, x:x+w　の順で設定
            org_imgBox = org_img[boxFromY: boxToY, boxFromX: boxToX]
            gray_imgBox = gray_img[boxFromY: boxToY, boxFromX: boxToX]
            canny_imgBox = canny_img[boxFromY: boxToY, boxFromX: boxToX]

            # ウィンドウに表示
            """
            cv2.namedWindow(ORGBOX_WINDOW_NAME)
            cv2.namedWindow(GRAYBOX_WINDOW_NAME)
            cv2.namedWindow(CANNYBOX_WINDOW_NAME)

            cv2.imshow(ORGBOX_WINDOW_NAME, org_imgBox)
            cv2.imshow(GRAYBOX_WINDOW_NAME, gray_imgBox)
            cv2.imshow(CANNYBOX_WINDOW_NAME, canny_imgBox)
            """

            # ファイルに保存
            cv2.imwrite(GRAYBOX_FILE_NAME, gray_imgBox)
            cv2.imwrite(CANNYBOX_FILE_NAME, canny_imgBox)

            # 終了処理
            cv2.waitKey(0)
            cv2.destroyAllWindows()


            """ HSVの値を取得 """
            # BGRからHSVに変換
            org_imgBoxHsv = cv2.cvtColor(org_imgBox, cv2.COLOR_BGR2HSV)

            # HSV平均値を取得
            # uHeは[0,179], Saturationは[0,255]，Valueは[0,255]
            #h = org_imgBoxHsv.T[0].flatten().mean()
            #s = org_imgBoxHsv.T[1].flatten().mean()
            v = org_imgBoxHsv.T[2].flatten().mean()

            """ エッジの量を取得 """
            # canny_imgBoxの画素値を取得
            # flattenで一次元化しmeanで平均を取得, [0,255]
            e = canny_imgBox.T.flatten().mean()

            """ リストに格納 """
            list_note.append([str(i)+str(j), v, e])

    return list_note

def GenDict(list_note):
    dict_note = {}
    a = 255 / 7 * 1.0

    for li_note in list_note:
        # ピッチ
        if li_note[1] <= a:
            note_tone = 'C5'
        elif li_note[1] <= 2*a:
            note_tone = 'D5'
        elif li_note[1] <= 3*a:
            note_tone = 'E5'
        elif li_note[1] <= 4*a:
            note_tone = 'F5'
        elif li_note[1] <= 5*a:
            note_tone = 'G5'
        elif li_note[1] <= 6*a:
            note_tone = 'A5'
        else:
            note_tone = 'B5'

        # 長さ
        """ 現在は固定 """
        note_length = 0.5

        # 辞書へ格納
        dict_note[li_note[0]] = [note_tone, note_length]

    print('')
    print('='*10 + ' dict_note ' + '='*10)
    pprint.pprint(dict_note)

    return dict_note

def MelodyAnchoring(dict_note):
    pass

def GenMIDI(dict_note, x_num, y_num, TEMPO, NUMERATOR, DENOMINATOR, path_output_melody_midi):

    def calc_notetime(tempo, numerator, denominator):
        notetime = [0] * 10
        j = 64
        for i in range(9):
            notetime[i+1] = 60*numerator*(1/j)/tempo
            j /= 2
        return notetime

    nt = calc_notetime(TEMPO, NUMERATOR, DENOMINATOR)
    d_time = nt[5] # コードを鳴らす間隔(nt[5]は4分音符)
    time = 0

    pm = pretty_midi.PrettyMIDI(resolution=960, initial_tempo=TEMPO)
    instrument = pretty_midi.Instrument(program=89, is_drum=False) # 89:synth pad(fantasia)

    for i in range(x_num):
        for j in range(y_num):
            note_name = dict_note[str(i)+str(j)][0]

            note_number = pretty_midi.note_name_to_number(note_name)

            note = pretty_midi.Note(velocity=100, pitch=note_number, start=time, end=time+d_time)
            instrument.notes.append(note)

            time = time + d_time

    pm.instruments.append(instrument)
    pm.write(path_output_melody_midi)

    print('')
    print('FInish generating MIDI file (melody) .')
