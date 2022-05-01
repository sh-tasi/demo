from flask import *
import boto3
from werkzeug.utils import secure_filename
import mysql.connector
import time
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=config['datakey']['aws_access_key_id'],
    aws_secret_access_key=config['datakey']['aws_secret_access_key'] 
)
dbconfig = {
    "host":config['datakey']['host'],
    "port":"3306",
    "user":config['datakey']['user'],
    "password":config['datakey']['password'],
    "database":"website"
}
cnx = mysql.connector.connect(pool_name = "mypool",
                              pool_size = 10,
                              pool_reset_session=True,
                              **dbconfig)
dataok=1
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/api/getdata",methods=["POST"])
def getdata():
    dataok=0
    content= request.form.get('content')
    #file=request.file
    #////以下取得檔案
    styleImage = request.files['imageFile']
    
    #////以下建立 S3 檔名時間序號
    nowTime = int(time.time())
    struct_time = time.localtime(nowTime)
    number = time.strftime("%Y%m%d%H%M%S", struct_time)
    
    #////以下為暫存檔案、讀取檔案
    #styleImage = request.files['imageFile'].read
    #styleImage = np.fromstring(styleImage, np.uint8)
    #file_name = styleImage.filename
    # tempFile = tempfile.TemporaryFile()
    # tempFile.write(styleImage.read())
    # print(tempFile.name)
    #styleImage = cv2.imdecode(styleImage, cv2.IMREAD_COLOR)[:,:,::-1]
    
    #////以下上傳檔案
    if styleImage:
    #     #filename= secure_filename(styleImage.filename)
    #     #////本地端檔案複寫
        myFilename= "test.jpg"
    #     #////雲端保持原黨名
        s3Filename= secure_filename(styleImage.filename)       
    #     #////存放圖片到本地端
        styleImage.save(myFilename)
        #print(filename)
        #print(tempFile.name)
        s3.upload_file(
            Bucket="shenghao",
            Filename=myFilename,
            Key= number+s3Filename,
        )
    cnx = mysql.connector.connect(pool_name = "mypool")
    cursor = cnx.cursor()
    sql="INSERT INTO `POST` (content,pictuer) VALUES(%s,%s)"
    val=(content,number+s3Filename)
    cursor.execute(sql, val)
    cnx.commit()
    cursor.close()  
    cnx.close()
    dataok=1
    reponse=jsonify({"ok":True})
    #print(styleImage)
    return(reponse)
@app.route("/api/getPoster",methods=["GET"])
def getPoster():
    if dataok==1:
        allPost=[]
        cnx = mysql.connector.connect(pool_name = "mypool")
        cursor = cnx.cursor()
        sql = "SELECT `id`,`content`,`pictuer` FROM `POST`" 
        cursor.execute(sql)    
        datas_field=list(zip(*cursor.description))[0]
        myresult=cursor.fetchall()
        for i in range(len(myresult)):
            post=dict(zip(datas_field,myresult[i]))
            allPost.append(post)
        reponse=jsonify({"data":allPost})
        cursor.close()  
        cnx.close()
        return(reponse)
app.run(host='0.0.0.0',port=5000)