from flask import Flask, render_template
from flask import request
import os
import pickle



import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.pipeline import Pipeline


#skimage
import skimage
import skimage.color
import skimage.transform
import skimage.feature




app=Flask(__name__)

BASE_PATH=os.getcwd()
UPLOAD_PATH=os.path.join(BASE_PATH,'static/upload/')
MODEL_PATH=os.path.join(BASE_PATH,'static/models/')



##----------------------Load model----------------------------

model_sgd_path=os.path.join(MODEL_PATH,'dsa_image_classification_sgd.pickle')
scaler_path=os.path.join(MODEL_PATH,'dsa_scaler.pickle')
model_sgd=pickle.load(open(model_sgd_path,'rb'))
scaler=pickle.load(open(scaler_path,'rb'))

@app.errorhandler(404)
def error404():
    render_template('error.html')

@app.errorhandler(405)
def error405():
    render_template('error.html')

@app.errorhandler (500)
def error500():
    render_template('error.html')




@app.route('/',methods=['GET','POST'])
def index():
    if request.method =='POST':
        upload_file=request.files['image_name']
        filename=upload_file.filename
        print('the file has been uploaded')
        ext=filename.split('.')[-1]
        print('extension of the file name ---> ', ext)
        if ext in ['png','jpg','jpeg']:
            #saving the image
            path_save=os.path.join(UPLOAD_PATH,filename)
            upload_file.save(path_save)
            print('file saved succesfully')
            #sent to pipeline model
            result=pipeline_model(path_save,scaler,model_sgd)
            hei=getheight(path_save)
            print(result)
            return render_template('upload.html',fileupload=True,extension=True,data=result,image_filename=filename,height=hei)

        else:
            print('use only the extension with png jpg')
            return render_template('upload.html',fileupload=False,extension=False)
    else:
        return render_template('upload.html')
    
@app.route('/about/')
def about():
    return render_template('about.html')

def getheight(path):
    img=skimage.io.imread(path)
    h,w,_=img.shape
    aspect= h/w
    given_width=300
    height=given_width*aspect
    return height






def pipeline_model(path,scaler_transform,model_sgd):
    #pipeline model
    image=skimage.io.imread(path)

    #transform 80x80

    image_resize =skimage.transform.resize(image,(80,80),anti_aliasing=True)
    image_rescale=255*image_resize

    #skimage.transform.rescale

    #image_downscaled = skimage.transform.downscale_local_mean(image, (4, 3))
    #image_rescale=skimage.transform.rescale(image,0.25,anti_aliasing=True)

    image_transform=image_rescale.astype(np.uint8)

    #rgb to gray

    gray=skimage.color.rgb2gray(image_transform)

    #hog feature

    feature_vector=skimage.feature.hog(gray,orientations=10,
                                pixels_per_cell=(8,8),
                                cells_per_block=(2,2))
    #scaling
    scalex=scaler.transform(feature_vector.reshape(1,-1))

    result=model_sgd.predict(scalex)
    #calculate probability # confidence
    decision_value=model_sgd.decision_function(scalex).flatten()
    labels=model_sgd.classes_
    
    #calculate z score
    z=scipy.stats.zscore(decision_value)
    prob_value=scipy.special.softmax(z)
    #top 5
    top_5_prob_ind=prob_value.argsort()[::-1][:5]
    top_labels=labels[top_5_prob_ind]
    top_prob=prob_value[top_5_prob_ind]
    # put in a dictionary
    top_dict=dict()
    for k,v in zip(top_labels,top_prob):
        top_dict.update({k:np.round(v,4)})
    
    

    return top_dict







if __name__=='__main__':
    app.run(debug=True)
























