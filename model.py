import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import numpy as np

path ="IMDB Dataset.csv"
df=pd.read_csv(path)

X,y=df.review,df.sentiment

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
vectorizer=CountVectorizer(stop_words='english')

X_train=vectorizer.fit_transform(X_train)
X_test=vectorizer.transform(X_test)

model=MultinomialNB()
model.fit(X_train,y_train)

y_pred=model.predict(X_test)
accuracy=accuracy_score(y_test,y_pred)
print(accuracy)