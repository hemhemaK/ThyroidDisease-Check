import joblib
import pandas as pd
import warnings

from django.http import request
from django.shortcuts import render
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')


def home(request):
        return render(request, 'index.html')


def predict(request):
        return render(request, 'predict.html')


df = pd.read_csv("dataset/df_resampled.csv")

x = df[['age', 'sex', 'on_thyroxine', 'query_on_thyroxine',
        'on_antithyroid_meds', 'sick', 'pregnant', 'thyroid_surgery',
        'I131_treatment', 'query_hypothyroid', 'query_hyperthyroid', 'lithium',
        'goitre', 'tumor', 'hypopituitary', 'psych', 'TSH_measured', 'TSH',
        'T3_measured', 'T3', 'TT4_measured', 'TT4', 'T4U_measured', 'T4U',
        'FTI_measured', 'FTI', 'TBG_measured','TBG']]
y = df[['target']]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
xgb = XGBClassifier()
xgb.fit(x_train, y_train)
y_pred = xgb.predict(x_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy:{accuracy}")

# save the model to disk
joblib.dump(xgb, "xgb_model.sav")
