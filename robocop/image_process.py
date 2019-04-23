import pdfquery
import xml.etree.ElementTree as et
from django.conf import settings
import os
import pandas as pd
from .models import Image
import json
from wand.image import Image as wi
import cv2
from .face_api import face_detect, face_verify

def processPdf(filename):
    pdfPath = settings.UPLOAD_DIR + '/' + filename
    pdfName, pdfExtension = os.path.splitext(filename)
    pdf = pdfquery.PDFQuery(pdfPath) # Fs_1.pdf is the name of the PDF
    pdf.load()
    pdf.tree.write(settings.PROCESS_DIR + '/' + pdfName + '.xml', pretty_print=True, encoding='UTF-8')
    tree = et.parse(settings.PROCESS_DIR + '/' + pdfName + '.xml')
    root = tree.getroot()
    keys = []
    values = []
    for movie in root.iter('Annot'):
        keys.append(movie.get("T"))
        values.append(movie.get("V"))
    dict_form = dict(zip(keys, values))
    
    df = pd.read_csv(settings.PROCESS_DIR + '/' + 'xml_def.csv')

    for i in range(df.shape[0]):
        df.loc[i, 'values'] = dict_form[df.loc[i, 'Tag']]

    df1 = df[['Def','values']]
    dict_form1 = dict(zip(df1['Def'], df1['values']))

    rowImage = Image(fileName = filename, values = json.dumps(dict_form1), image = '', flag = 'G')
    rowImage.save()

    df2 = pd.read_csv(settings.PROCESS_DIR + '/' + 'master.csv')
    for i in range(df2.shape[0]):
        a = df.loc[df['Def'] == df2.loc[i, 'Def']].index[0]
        df2.loc[a, 'file'] = df.loc[a, 'values']
        
    for z in range(df2.shape[0]):
        if df2.loc[z, 'values'] == df2.loc[z, 'file']:
            df2.loc[z, 'score'] = 1
        else:
            df2.loc[z, 'score'] = 0
            
    total_acc = df2['score'].sum() / df2.shape[0]

    print(df2)
    json_df2 = df2.to_json(orient='records')

    pdf = wi(filename = pdfPath, resolution = 300)
    pdfImage = pdf.convert('jpeg')
    i = 1
    for img in pdfImage.sequence:
        page = wi(image = img)
        page.save(filename = settings.PROCESS_DIR + '/' + pdfName + '_' + str(i) + '.jpg')
        i += 1

    image = cv2.imread(settings.PROCESS_DIR + '/' + pdfName + '_' + "1.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(image, 10, 250)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    dilated = cv2.dilate(edged, kernel, iterations = 5)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    (_, cnts, _) = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    idx = 5
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w > 200 and h > 200 and w < 500 and h < 500:
            idx += 1
            new_img = image[y:y+h, x:x+w]
            cv2.imwrite(settings.PROCESS_DIR + '/' + pdfName + '_' + str(idx) + '.jpg', new_img)

    rowImage.image = pdfName + '_' + str(idx) + '.jpg'
    rowImage.save()

    face1 = face_detect(settings.PROCESS_DIR + '/' + 'master.jpg')
    face2 = face_detect(settings.PROCESS_DIR + '/' + rowImage.image)

    res = {}
    if face1 != {} and face2 != {}:
        res = face_verify(face1[0]['faceId'], face2[0]['faceId'])

    if res != {}:
        ret = {}
        ret['accuracy'] = total_acc
        ret['image'] = rowImage.image
        ret['match'] = res['confidence']
        ret['ismatch'] = res['isIdentical']
        ret['score'] = json_df2

        return ret

    return res
