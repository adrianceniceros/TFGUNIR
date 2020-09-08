import re
import nltk
from sklearn.datasets import load_files
import pickle
from nltk.corpus import stopwords

#cargar el dataset de pruebas

email_data = load_files("./TEXT",encoding="UTF8")
X, y = email_data.data, email_data.target


#procesarlo hasta conseguir textos limpios tokenizados en una lista documents de elementos document
documents = []

from nltk.stem import WordNetLemmatizer

stemmer = WordNetLemmatizer()


for sen in range(0, len(X)):
    # Remove all the special characters
    document = re.sub(r'\W', ' ', str(X[sen]))
    
    # remove all single characters
    document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
    
    # remove line break
    document = re.sub(r'\\n', ' ', document)
    
    # remove underscore
    document = re.sub(r'_', '', document)
    
    # Remove numbers
    document = re.sub(r'[0-9]', ' ', document) 
    
    # Remove single characters from the start
    document = re.sub(r'\^[a-zA-Z]\s+', ' ', document) 
    
    # Substituting multiple spaces with single space
    document = re.sub(r'\s+', ' ', document, flags=re.I)
    
    # Removing prefixed 'b'
    document = re.sub(r'^b\s+', '', document)
    
    # Converting to Lowercase
    document = document.lower()
    
    # Lemmatization
    document = document.split()

    document = [stemmer.lemmatize(word) for word in document]
    document = ' '.join(document)
    
    documents.append(document)


sr = stopwords.words('spanish')
customstopwords = ["ab", "agradecería", "ahora", "alguna", "alguno", "algún", "arsys", "asi", "asunto", "así", "ayer", "ayuda", "buenos", "cada", "cm", "com", "content", "continuación", "cualquier", "después", "do", "días", "estimado", "etc", "favor", "for", "fra", "fri", "gracias", "hola", "img", "jan", "miércoles", "nurialorenzoc", "of", "ra", "rsa", "saludo", "si", "tambien", "tardes", "the", "to", "va", "viernes"]
for word in customstopwords:    
    sr.insert(0,word)    

#convertir texto a números con bag of words
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(max_features=1500, min_df=3, max_df=0.7, stop_words=sr)
X = vectorizer.fit_transform(documents).toarray()


vectorizer2 = CountVectorizer(max_features=1500, min_df=3, max_df=0.7, stop_words=sr)
X2 = vectorizer2.fit_transform(documents)
print(vectorizer2.get_feature_names()) #las palabras que quedan en la bolsa

#print(vectorizer2.inverse_transform(X2))
array_palabras = vectorizer2.get_feature_names()

    
    


#Finding TFIDF
from sklearn.feature_extraction.text import TfidfTransformer
tfidfconverter = TfidfTransformer()
X = tfidfconverter.fit_transform(X).toarray()

#Training and Testing Sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

#X_pred, X_test, y_pred, y_test = train_test_split(X_test, y_test, test_size=0.8, random_state=0)


#Training Text Classification Model and Predicting Sentiment
from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators=1000, random_state=0)
classifier.fit(X_train, y_train) 

y_pred = classifier.predict(X_test)


# COMPROBACIONES DE COMO FUNCIONA EL MODELO
#https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
confusionmatrix = confusion_matrix(y_test,y_pred)

print ()
print ("Test con el 20% (" + str(len(y_test)) + ") del total de la muestra (" + str(len(X)) + ")")
print ("Ocurrencias del grupo 0 que clasifican como 0: ", confusionmatrix[0][0])
print ("Ocurrencias del grupo 0 que clasifican como 1: ", confusionmatrix[0][1]) 
print ("Ocurrencias del grupo 1 que clasifican como 0: ", confusionmatrix[1][0]) 
print ("Ocurrencias del grupo 1 que clasifican como 1: ", confusionmatrix[1][1]) 
print ()

# https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html#sklearn.metrics.precision_recall_fscore_support
print(classification_report(y_test,y_pred))

#https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html
print(accuracy_score(y_test, y_pred))

with open('text_classifier', 'wb') as picklefile:
    pickle.dump(classifier,picklefile)
    
with open('documents', 'wb') as picklefile:
    pickle.dump(documents,picklefile)