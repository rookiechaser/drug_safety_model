import io
from flask import Flask,render_template,request,send_file
import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_restful import Resource
import pickle
import csv
import matplotlib.pyplot as plt
import joblib
import json
import qrcode
import zipfile


app=Flask(__name__)
model = pickle.load(open("random_forest_model.pkl", "rb"))


@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        file1=request.files['test1']
        filepath=os.path.join(file1.filename)
        file1.save(filepath)
        return 'file uploaded and saved successfully'
    return render_template('index.html')
@app.route('/data',methods=['GET','POST'])
def data():
    if request.method=='POST':
        data_safe=[]
        # test=pd.read_csv('test.csv')
        test=pd.read_csv('test.csv')
        # Pre Process Check
        test['strength'] = test['strength'].str.extract('(\d+)').astype(int)
        columns_to_convert = ['api_water', 'api_total_impurities', 'api_l_impurity', 'api_ps01', 'api_ps05', 'api_ps09']

        for column in columns_to_convert:
    
            test[column] = test[column].apply(lambda x: float(x) if x.strip() != '' else None)

        test=pd.DataFrame(test,dtype=float)
        #test
        test["api_water"].fillna( method ='ffill',inplace=True)
        test["api_total_impurities"].fillna( method ='ffill',inplace=True)
        test["api_l_impurity"].fillna( method ='ffill',inplace=True)
        test["api_ps01"].fillna( method ='ffill',inplace=True)
        test["api_ps05"].fillna( method ='ffill',inplace=True)
        test["api_ps09"].fillna( method ='ffill',inplace=True)

        prediction = model.predict(test)
        for i in prediction:
            if(i == 1):
                data_safe.append("safe")
            else:
                 data_safe.append("unsafe")
        datas_n=pd.DataFrame(data_safe,columns=['safety'])
        final=pd.concat([test[['batch','code','resodual_solvent','impurities_total']], datas_n], axis=1)
        final.columns=['batch','code','resodual_solvent','impurities_total','safety']
        qr_generation=final[final['safety']=='safe']
        # storing data in JSON format
        qr_generation.to_json('file1.json', orient = 'split', compression = 'infer')
        return render_template('data.html', data= final.to_html(header=True, index=False))
@app.route('/download',methods=['GET','POST'])
def download():
    # Opening JSON file
    f = open('file1.json')

    # returns JSON object as
    # a dictionary
    data_store = json.load(f)
    # Assuming you already have your data_store with 'data' as a list of dictionaries

    # Create a directory to save QR code images
    if not os.path.exists("qr_images"):
        os.mkdir("qr_images")

    # Loop through the data and generate QR codes
    for i in data_store['data']:
        keys = ['batch', 'code', 'resodual_solvent', 'impurities_total', 'safety']
        values = i
        my_dict = {keys[i]: values[i] for i in range(len(keys))}
        json_string = json.dumps(my_dict)
    
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add the JSON data to the QR code
    qr.add_data(json_string)
    qr.make(fit=True)

    # Create an image from the QR code instance
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image
    image_filename = os.path.join("qr_images", "batch" + str(i[0]) + ".png")
    qr_image.save(image_filename)

    #print("QR code images generated with JSON data embedded.")

    # Create a ZIP archive of the generated QR code images
    with zipfile.ZipFile("qr_images.zip", "w") as zipf:
        for root, _, files in os.walk("qr_images"):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.basename(file_path))
    path = 'qr_images.zip'
    return send_file(path, as_attachment=True)
    #print("QR code images saved as qr_images.zip")




if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
