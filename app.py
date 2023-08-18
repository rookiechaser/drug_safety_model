from flask import Flask,render_template,request
import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_restful import Resource
import pickle
import csv
import matplotlib.pyplot as plt
import joblib



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
        return render_template('data.html',data= final.to_html(header=True,index=False))




if __name__=='__main__':
    app.run(debug=True)
