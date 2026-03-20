from flask import Flask,request,render_template,redirect,url_for, jsonify,g , send_file, make_response
from io import BytesIO
import base64
from PIL import Image
import os
import cv2
import zipfile
import numpy as np
from datetime import datetime
from add_watermark_invis import add_invis,search_invis
from add_watermark import add_vis,add_vis_img
from test2 import predict
from visible_watermark_detect import check_vis
from hidden_data_detect import hid_data
from add_visible_doc import add_vis_pdf,add_vis_doc
from template_detect import template_det
from check_doc import detect_watermark_docx,detect_watermark_pdf
from add_exif_data import add_exif
from invisible_watermark_detext import invis_test
import sqlite3
from docx import Document
from docx.shared import Inches
#database connection
def connect_db():
    db_path = os.getenv("DB_PATH", "data.db")
    sql=sqlite3.connect(db_path,timeout=30)
    cur=sql.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.close()
    sql.row_factory=sqlite3.Row
    return sql 
def get_db():
    if not hasattr(g,'sqlite3' ):
        g.sqlite_db=connect_db()
    return g.sqlite_db

#def get_db_connection():
    #sql=sqlite3.connect('')
    #sql.row_factory=sqlite3.Row
    #return sql
    #conn = psycopg.connect(dbname="watermark",user="postgres",password="shive",host="localhost")
    #cur=conn.cursor()
    #return cur,conn

#def get_db():
    #if not hasattr(g,'sqlite3'):
    #    g.sqlite_db=get_db_connection()
    #return g.sqlite_db



app=Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()
#index
@app.route('/',methods=['post','get'])
def index():
    return redirect(url_for('login'))

#login page
@app.route('/login',methods=['post','get'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        passwd=request.form.get('password')
        cur=get_db()
        data=cur.execute('Select password from users where username=?',(username,))
        try:
            
            data=data.fetchone()
            if data is None:
                raise KeyError
        except:
            return redirect(url_for('login'))
        cur.close()
        print(username)
        if data['password']==passwd:
            print(data['password'])
            return redirect(url_for('indx',username=username))
        else:
            return redirect(url_for('login'))
        
    return render_template('login.html')

#signup page
@app.route('/signup',methods=['post','get'])
def signup():
    if request.method=='POST':
   
        username=request.form.get('username')
        passwd=request.form.get('password')

        cur=get_db()
        try:
            data=cur.execute('select * from users where username=(?)',(username,)).fetchall()
        except:
            data=None
        if data:
            cur.close()
            
            return 'ALREADY EXISTS'
        else:
            cur.execute('insert into users(username,password) values((?),(?))',(username,passwd))
            cur.commit()
            cur.close()
           
        return redirect(url_for('login'))
    return render_template('signup.html')

#REDIRECTS
@app.route('/addwa/')
@app.route('/addwa/<username>')
def addwa(username='guest'):
    if request.method=='POST':
        return render_template('addnew.html',username=username)
    return render_template('addnew.html',username=username)
@app.route('/indx/')
@app.route('/indx/<username>')
def indx(username='guest'):
    if request.method=='POST':
        return render_template('home.html',username=username)
    return  render_template('home.html',username=username)

@app.route('/docu')
@app.route('/docu/<username>')
def docu(username='guest'):
    return render_template('adddoc.html',username=username)
#after login/signup home page
@app.route('/all/')
@app.route('/all/<username>',methods=['post','get'])
def all(username='guest'):
    if request.method=='POST':
        dic={}
        now=datetime.now()
        
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        img_og=request.files['image']
        nparr = np.frombuffer(img_og.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        output=predict(img)
        if output[0] > 0.5:
            dic['watermark']=f"LIKELY WATERMARK PRESENT WITH {output[0]*100} % CONFIDENCE"
        else:
            dic['watermark']=f"NO WATERMARK DETECTED WITH {output[1]*100} % CONFIDENCE"
        score=invis_test(img)
        if score==1:
            dic['invisible watermark']=f"LOW CHANCES OF INVISIBLE WATERMARK"
        elif score==2:
            dic['invisible watermark']=f"HIGH CHANCES OF INVISIBLE WATERMARK"
        else:
            pass
        op1,op2,output2=check_vis(img)
        dic['visible watermark clear']=op1
        dic['visible watermark unclear']=op2
        op3,output3=hid_data(img)
        dic['exif_data']=output3
        dic['hidden zip file']=op3
        img_og.seek(0)
        img_bytes = img_og.read()
        if username!='guest':
            typ='.png'
            cur=get_db()
            d=cur.execute('select id from users where username=(?)',(username,)).fetchone()
            user=d['id']
            cur.execute("insert into datas(id,image,query,type,created_at) values((?),(?),(?),?,?)",(user,sqlite3.Binary(img_bytes),str(dic),typ,date))
            cur.commit()
            cur.close()
        _,buffer=cv2.imencode('.png',output2)
        img_base64=base64.b64encode(buffer).decode('utf-8')

        return jsonify({'query':dic,'image':img_base64})
    return render_template('analyzer.html',username=username)

#search invisible 
@app.route('/search/')
@app.route('/search/<username>',methods=['post','get'])
def search(username='guest'):
    if request.method=='POST':
       
        if username=='guest':
            return redirect(url_for('login'))
        cur=get_db()
        img=request.files['image']
        filename=img.filename
        nparr = np.frombuffer(img.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        secret_key=request.form.get('key')
        _, buffer = cv2.imencode(".png", img)
        img_bytes = buffer.tobytes()
        data2=cur.execute('select id from users where username=?',(username,)).fetchone()
        data=cur.execute('select * from secure_image where id2=?',(secret_key,)).fetchone()
        if data is None:
            return jsonify({'output':'invalid security key'})
        nparr = np.frombuffer(data['images'], np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        _,buffer2=cv2.imencode('.png',img)
        img_bytes2=buffer2.tobytes()
        if data['images'] is None:
            return jsonify({'output':'invalid security key'})
        elif data['id']!=data2['id']:
            return jsonify({'output':'invalid security key'})
        elif img_bytes2!=img_bytes:
            return jsonify({'output':'invalid security key'})
        cur.close()
        secret_key=data['secret_key']
        ans= search_invis(img,secret_key)
        if ans is None:
            ans='null'
        
        print(filename)
        print(ans)
        print(jsonify({str(filename):str(ans)}))
        return jsonify({str(filename):str(ans)})
        #return render_template('search.html',secret_key=secret_key)
    return render_template('detectinvis.html',username=username)

#template detection 
@app.route('/template/')
@app.route('/template/<username>',methods=['post','get'])
def temp(username='guest'):
    if request.method=='POST':
        img1=request.files['template_image']
        img2=request.files.getlist('main_image')
        dic={}
        img_bytes=None
        now=datetime.now()
        
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        for i in img2:
            dic[i.filename]=template_det(i,img1)
            i.seek(0)
            img_bytes=i.read()
        if username!='guest':
            typ='.png'
            cur=get_db()
            d=cur.execute('select id from users where username=(?)',(username,)).fetchone()
            user=d['id']
            cur.execute("insert into datas(id,image,query,type,created_at) values((?),(?),(?),?,?)",(user,sqlite3.Binary(img_bytes),str(dic),typ,date))
            cur.commit()
            cur.close()

        return jsonify(dic)
    return render_template('template.html',username=username)

#redirect from home page to add visible tag
#WARNING visible watermarks cannot be removed
@app.route('/add/')
@app.route('/add/<username>',methods=['post','get'])
def add(username='guest'):
    options={'opacity':['bold','transparent','invisible'],'position':['center','center-right','center-left','center-bottom','center-top'],'font':['BROADW.TTF','ARLRDBD.TTF','BASKVILL.TTF','CASTELAR.TTF','CENTURY.TTF']}
    if request.method=='POST':
    
        smth=request.files['file']
        
        now=datetime.now()
        
        date = now.strftime("%Y-%m-%d %H:%M:%S")
    
        img=smth
        img.seek(0)
        type2=request.form.get('type')
        text=request.form.get('text')
        position=request.form.get('position')
        font=request.form.get('font')
        opacity=request.form.get('opacity')
        print(opacity)
        size=request.form['fontSize']
        grid=request.form.get('pattern')
        if grid=='grid':
            grid=True
        else:
            grid=False
        x,y=0,0
        size=int(size)
        if type2=='text':
            image=add_vis(img,text,x,y,font,grid,round(float(opacity),0)*100,size)
        else:

            img2=request.files.get('logo')
            image=add_vis_img(img,img2,x,y,round(float(opacity),0)*100,grid)
        image=add_exif(image,date)
        if username!='guest':
            typ=None
            cur=get_db()
            img_bytes=None
            
            _, buffer = cv2.imencode(".png", image)
            img_bytes = buffer
            typ='.png'
            d=cur.execute('select id from users where username=?',(username,)).fetchone()
            user=d['id']
            cur.execute('insert into datas(id,image,added_watermark,type,created_at) values((?),(?),(?),?,?)',(user,sqlite3.Binary(img_bytes),text,typ,date))
            cur.commit()
            cur.close()
            
        buf = BytesIO() 
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image=Image.fromarray(image)
        print(image)
        image.save(buf, format="PNG")
        buf.seek(0)
        print(buf)
        return send_file(buf,mimetype='image/png',as_attachment=True,download_name='image.png')
   
    return render_template('add.html',options=options,username=username)

@app.route('/adddoc/')
@app.route('/adddoc/<username>',methods=['post','get'])
def adddoc(username='guest'):
    options={'small':30,'medium':50,'large':80,'transparent':100,'bold':255,'invisible':30}
    if request.method=='POST':
        smth=request.files['files']
        now=datetime.now()
        
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        if smth.filename.lower().endswith('.pdf'):
            pdf=smth
            pdf.seek(0)
            text=request.form.get('text')
            font=request.form.get('font')
            opacity=request.form.get('opacity')
            size=request.form['size']
            size=options[size]
            opacity=options[opacity]
            image=add_vis_pdf(pdf,text,font,opacity,size)
            
        elif smth.filename.lower().endswith('.doc') or smth.filename.lower().endswith('.docx'):
            doc=smth
            doc.seek(0)
            text=request.form.get('text')
            font=request.form.get('font')
            opacity=request.form.get('opacity')
            size=request.form['size']
            size=options[size]
            opacity=options[opacity]
            image=add_vis_doc(doc,text,font,opacity,size)
        if username!='guest':
            typ=None
            cur=get_db()
            img_bytes=None
            if smth.filename.lower().endswith('.pdf'):
                typ='.pdf'
                img_bytes = image.read()
                
            else:
                typ='.docx'
                img_bytes=image.read()
            
            d=cur.execute('select id from users where username=?',(username,)).fetchone()
            user=d['id']
            cur.execute('insert into datas(id,image,added_watermark,type,created_at) values((?),(?),(?),?,?)',(user,sqlite3.Binary(img_bytes),text,typ,date))
            cur.commit()
            cur.close()
            
        buf = BytesIO()
        if smth.filename.lower().endswith('.pdf'):
            image.seek(0)
            
            return send_file(
            image,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="file.pdf"
            )
        else:
            image.seek(0)
            
            doc_obj = Document(image)
            buf = BytesIO()
            doc_obj.save(buf)
            buf.seek(0)

            return send_file(
                buf,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                as_attachment=True,
                download_name="file.docx"
            )
    return render_template('visibledoc.html',username=username)
         
#WARNING invisible watermarks cannot be removed
@app.route('/addinvis/')
@app.route('/addinvis/<username>',methods=['post','get'])
def addinvis(username='guest'):
    if request.method=='POST':
        if username=='guest':
            return redirect(url_for('login'))
        now=datetime.now()
        
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        img=request.files['image']
        security_key=request.form.get('key')
        _,img=cv2.imencode('.png',img)
        img_bytes=img.tobytes()
        op=invis_test(img_bytes)
        if op>=1:
            return jsonify({'invalid':'hidden watermark already present'})
        img,key=add_invis(img,security_key)
        #key=len(key)
        data=None
        if username!='guest':
            typ='.png'
            cur=get_db()
            
            _, buffer = cv2.imencode(".png", img)
            img_bytes = buffer.tobytes()
            d=cur.execute('select id from users where username=(?)',(username,)).fetchone()
            user=d['id']

            cur.execute('insert into datas(id,image,added_watermark,type,created_at) values((?),(?),(?),?,?)',(user,sqlite3.Binary(img_bytes),security_key,typ,date))
            cur.execute('insert into secure_image(id,images,secret_key,created_at) values(?,?,?,?)',(user,sqlite3.Binary(img_bytes),key,date))
            data=cur.execute('select id2 from secure_image where created_at=?',(date,)).fetchone()
            cur.commit()
            cur.close()
        str2=f"key={data['id2']}"
        fil=BytesIO(str2.encode('utf-8'))
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _,buffer=cv2.imencode('.png',img_rgb)
        img_bytes=buffer.tobytes()
        memry=BytesIO()
        zf=zipfile.ZipFile(memry,'w')
        zf.writestr('key.txt',fil.getvalue())
        zf.writestr('image.png',img_bytes)
        zf.close()
        memry.seek(0)
        return send_file(memry, mimetype="application/zip", as_attachment=True,download_name='encrypt.zip')
       
    return render_template('addinvis.html',username=username)

#based on userid display history
#THE POST METHOD IS NOT ACCESSED, API CALL ONLY
@app.route('/history/')
@app.route('/history/<username>')
def history(username='guest'):
    if request.method=='POST':
        month=None
        day=None
        if request.method=='POST':
            month = request.args.get("month").zfill(2)
            day = request.args.get("day").zfill(2)
        
        cur=get_db()
        try:
            data=cur.execute('select * from users where username=(?)',(username,)).fetchone()
        except:
            data=None
        if data:
            if month and day:
                data=cur.execute('select * from datas join users on datas.id=users.id where users.username=(?) and strftime("%m-%d",created_at)=?',(username,f"{month}-{day}")).fetchall()
                data2=cur.execute('select * from documents join users on documents.id where users.username=(?) and strftime("%m-%d",created_at)=?',(username,f"{month}-{day}")).fetchall()
            else:
                data=cur.execute('select * from datas join users on datas.id=users.id where users.username=(?)',(username,)).fetchall()
                data2=cur.execute('select * from documents join users on documents.id where users.username=(?)',(username,)).fetchall()
            cur.close()
        else:
            return redirect(url_for('login'))
    return render_template('history.html',username=username)

#documents and pdf option
@app.route('/docorpdf/')   
@app.route('/docorpdf/<username>',methods=['POST','GET'])
def docorpdf(username='guest'):
    if request.method=='POST':
        pdf=request.files['file']
        word=request.form.get('word')
        cur=get_db()
        now=datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        if pdf.filename.lower().endswith(".pdf"):
            print('hello')
            typ='.pdf'
            dic1,dic2,dic3=detect_watermark_pdf(pdf,word)
            d=cur.execute('select id from users where username=(?)',(username,)).fetchone()
            user=d['id']
            cur.execute('insert into datas(id,image,query,type,created_at) values(?,?,?,?,?)',(user,sqlite3.Binary(pdf.read()),str([dic1,dic2,dic3]),typ,date))
            cur.commit()
            cur.close()
            return jsonify({'output':[dic1,dic2,dic3]})
        elif pdf.filename.lower().endswith(".docx") or pdf.filename.lower().endswith(".doc"):
            typ='.docx'
            if pdf.filename.lower().endswith(".doc"):
                return 'please upload a .docx file'
            dic1,dic2=detect_watermark_docx(pdf,word)
            d=cur.execute('select id from users where username=?',(username,)).fetchone()
            user=d['id']
            cur.execute('insert into datas(id,image,query,type,created_at) values(?,?,?,?,?)',(user,sqlite3.Binary(pdf.read()),str([dic1,dic2]),typ,date))
            cur.commit()
            cur.close()
            return jsonify({'output':[dic1,dic2]})
        
    return render_template('updoc.html',username=username)

#api calls for user history
@app.route("/api/hist/<username>", methods=["GET"])
def hist(username):
    conn = get_db()
    cur = conn.cursor()
    id=cur.execute('select id from users where username=?',(username,)).fetchone()
    id=id['id']
    cur.execute("SELECT * FROM datas where id=? ORDER BY created_at DESC ",(id,))
    rows = cur.fetchall()
    conn.close()
    data = []
    for r in rows:
      
        item = {
            "id": r["id2"],
            "type": r["type"],
            "created_at": r["created_at"],
            "query": r["query"],
            'added_watermark':r['added_watermark']
        }
        if r["type"] == ".png":
            item["image"] = base64.b64encode(r['image']).decode("utf-8")
            item["preview_url"] = f"/api/preview/{r['id2']}"
        if r["type"] == ".pdf" or r['type']=='.docx':
            item["image"] = base64.b64encode(r['image']).decode("utf-8")
        data.append(item)
    return jsonify(data)

@app.route("/api/hist2/<username>")
def get_history_preview(username):
    conn = get_db()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if not user:
        return jsonify([])

    user_id = user["id"]

    rows = cur.execute("""
        SELECT image, created_at, added_watermark, query,type
        FROM datas
        WHERE id=?
        ORDER BY created_at DESC
        LIMIT 3
    """, (user_id,)).fetchall()

    conn.close()

    result = []

    for r in rows:
        # convert bytes → base64 string
        img_base64 = base64.b64encode(r["image"]).decode("utf-8")
        if r['type']=='.png':
            result.append({
                "image": f"data:image/png;base64,{img_base64}",
                "created_at": r["created_at"],
                "added_watermark": r["added_watermark"],
                "query": r["query"]
            })
        elif r['type']=='.pdf':
            result.append({
                "image": "pdf",
                "created_at": r["created_at"],
                "added_watermark": r["added_watermark"],
                "query": r["query"]
            })
        else:
            result.append({
                "image": "docx",
                "created_at": r["created_at"],
                "added_watermark": r["added_watermark"],
                "query": r["query"]
            })
    return jsonify(result)
#api call for user history image preview
@app.route("/api/preview/<int:id>")
def preview_image(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT image,id2 FROM datas WHERE id2=?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return "Not found", 404
    return send_file(
        BytesIO(row["image"]),
        mimetype="image/png"
    )
@app.route("/api/preview2/<username>")
def preview_image2(username):
    conn = get_db()
    cur = conn.cursor()
    data=cur.execute('select id from users where username=?',(username,)).fetchone()
    id=data['id']
    cur.execute("SELECT image,id2 FROM datas WHERE id=?  order by created_at DESC limit 3", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return "Not found", 404
    return send_file(
        BytesIO(row["image"]),
        mimetype="image/png"
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)