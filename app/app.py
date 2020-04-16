import os, sys
import json
from app.model.Image2melody import Image2melody_script
from app.model.Melody2Chords import Melody2Chords_script

from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename # ファイル名をチェックする関数
from PIL import Image

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
print(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

#Flaskオブジェクトの生成
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ファイル容量制限 : 1MB
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# .があるかどうかのチェックと、拡張子の確認をする関数
# OKなら１、だめなら0
def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# '/' へのアクセス
@app.route('/')
def index():
    return redirect(url_for('predict'))

# '/predict' へのアクセス
@app.route('/predict', methods=['GET', 'POST'])
def predict():

    # POST
    if request.method == 'POST':

        # ファイルが読み込まれていない場合は'/predict'に戻る
        if 'file' not in request.files:
            flash('No file.')
            return redirect(url_for('predict'))

        # ファイルが読み込まれている場合はそのファイルを読み込む
        file = request.files['file']
        if file.filename == '':
            flash('No file.')
            return redirect(url_for('predict'))

        # 読み込んだファイルを処理する
        if file and is_allowed_file(file.filename):

            # 安全なファイル名を作成して画像ファイルを保存
            filename = secure_filename(file.filename)
            #filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            filepath = filename
            file.save(filepath)

            # midiファイル(melody)生成
            dict_note = Image2melody_script.model(filepath)
            # midiファイル(melody+chords)生成
            Melody2Chords_script.model_test(dict_note)

            # 画像ファイルを削除する
            os.remove(filepath)

            #return render_template('result.html', pred_argmax=pred_argmax)
            return render_template('result.html')

    return render_template('predict.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# デバッグ中にCSSをキャッシュせず瞬時に値を反映する
@app.context_processor
def add_staticfile():
    def staticfile_cp(fname):
        path = os.path.join(app.root_path, 'static', 'css', fname)
        mtime =  str(int(os.stat(path).st_mtime))
        return '/static/css/' + fname + '?v=' + str(mtime)
    return dict(staticfile=staticfile_cp)

if __name__ == "__main__":
    #app.run(debug=True)
    app.run()
