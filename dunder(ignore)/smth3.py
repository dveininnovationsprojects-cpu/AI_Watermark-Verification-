import cv2
from io import BytesIO
from flask import send_file,Flask
import zipfile
fil=BytesIO(b'hello')
img_rgb = cv2.imread(r'd:\watermark.png')
_,buffer=cv2.imencode('.png',img_rgb)
img_bytes=buffer.tobytes()
memry=BytesIO()
zf=zipfile.ZipFile(memry,'w')
zf.writestr('key.txt',fil.getvalue())
zf.writestr('image.png',img_bytes)
zf.close()
memry.seek(0)
print(memry)
app=Flask(__name__)
@app.route('/')
def idex():
    return send_file(memry, mimetype="application/zip", as_attachment=True,download_name='encrypt.zip')
if __name__=='__main__':
    app.run(debug=True)