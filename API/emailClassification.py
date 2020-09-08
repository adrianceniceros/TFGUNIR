import re
import os
import datetime
import connections as cn

import email
import mailparser

from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestClassifier

from collections import OrderedDict

import json

import pickle


class AnalyzedMail:
    """Data structure to store all analyzed email data.

    Attributes:
        from (str): from field from analyzed email.
        to (str): to field from analyzed email.
        subject(str): subject from analyzed email.
        mainText(str): text from analyzed email.
        urls([str]): list of URLs contained at the email.
        tokens([str]): list of tokens contained at the email.
        isPhishing(int): 0 if the email does not contain phishing URLs - 1 if email contain phishing URLs.
        predDpto(str): name of the predicted department.
        predProb(int): 0 to 100 percentage - confidence with the prediction.

    Args:
        content (str): the full text content to analyze.
        mode (int): the mode to use in the analisys.
            mode 0: full email with headers.
            mode 1: only text to classify mode.

    """
    def __init__(self, content, mode):
        try:
            if (mode == 0):
                mail = mailparser.parse_from_string(content)
                self._from = mail.from_
                self._to = mail.to
                self._subject = mail.subject
                self._mainText = parse_mainText(mail.text_plain[0])
                self._urls = extract_urls(str(content))
                self._tokens = tokenize(self._mainText)
                self._isPhishing = isPhishing(self._urls)
                prediction = selectDpt(self._mainText)
                self._predDpto = prediction.getDpto()
                self._predProb = prediction.getProb()

            elif (mode == 1):
                self.mainText = content
                self._urls = extract_urls(str(content))
                self._tokens = tokenize(content)
                self._isPhishing = 0
                prediction = selectDpt(content)
                self._predDpto = prediction.getDpto()
                self._predProb = prediction.getProb()
        except:
            raise

    def getText(self):
        return(self._mainText)

    def getFrom(self):
        return(self._from[0])

    def getTo(self):
        return(self._to[0])

    def getSubject(self):
        return(self._subject)

    def getDpto(self):
        return(self._predDpto)

    def getProb(self):
        return(self._predProb)

    def getPhish(self):
        return(self._isPhishing)



class Prediction:
    """Data structure to store one prediction once done.

    Attributes:
        dpto(str): name of the predicted department.
        prob(int): 0 to 100 percentage - confidence with the prediction.

    Args:

    """
    def __init__(self):
        self._dpto = " "
        self._prob = "0"

    def setDpto(self, dpto):
        self._dpto = dpto

    def setProb(self, prob):
        self._prob = prob

    def getDpto(self):
        return(self._dpto)

    def getProb(self):
        return(self._prob)



def extract_urls(rawtext):
    """Extract all urls detected with regular expressions at a given text.

    Args:
        rawtext(str): the text where the URLs should be found.

    Returns:
       A list with de detected URLs.

    Raises:
        Generic error if occours.
    """
    try:
        #extract URLs with REGEX
        urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2})).*', rawtext) 


        for posicion, url in enumerate(urls):
            urls[posicion] = urls[posicion].split("/")[2]
            urls[posicion] = urls[posicion].split('\'')[0] #split some chars that mark the end of the domain
            urls[posicion] = urls[posicion].split('\"')[0]
            urls[posicion] = urls[posicion].split('>')[0]


        urls = list(dict.fromkeys(urls)) #delete duplicates

        return(urls)

    except:
            raise



def extract_emails(rawtext): #currently not used by the API
    """Extract all emails detected with regular expressions at a given text.

    Args:
        rawtext(str): the text where the emails should be found.

    Returns:
       A list with de detected emails.
    """
    emails = re.findall('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', rawtext) #extract emails with REGEX

    emails = list(dict.fromkeys(emails)) #delete duplicates

    return(emails)



def extract_domains(rawtext): #currently not used by the API
    """Extract all domain names detected with regular expressions at a given text.

    Args:
        rawtext(str): the text where the domain name should be found.

    Returns:
       A list with de detected URLs.

    """
   #extract domains with REGEX
    dominios = re.findall('[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}', rawtext)
    i=0

    for dominio in dominios:
        dominio = dominio('\'')[0] #split some chars that mark the end of the domain
        dominio = dominio('\"')[0]
        dominio = dominio('>')[0]
    dominios = list(dict.fromkeys(dominios)) #elimina duplicados

    return(dominios)



def parse_mainText(rawtext): 
    """ Get de main text of a given EML structure, avoiding the thread composed by answers or resends.

    Args:
        rawtext(str): the text with standard EML format.

    Returns:
       The main text of a query.

    """
    texto_primermensaje = ""
    cuenta = 0
    for line in rawtext.splitlines(): #split when end string appears
        cuenta = cuenta+1
        buscador = line.find("Inicio del mensaje reenviado")
        if buscador >= 0:
            break
        buscador = line.find("-- Mensaje Original --")
        if buscador >= 0:
            break
        buscador = line.find("--- mail_boundary ---")
        if buscador >= 0:
            break
        buscador = line.find("ADVERTENCIA LEGAL")
        if buscador >= 0:
            break
        buscador = line.find("LEGAL WARNING")
        if buscador >= 0:
            break
        buscador = line.find("Aviso Legal")
        if buscador >= 0:
            break
        buscador = line.find("Advertencia legal")
        if buscador >= 0:
            break

        texto_primermensaje = texto_primermensaje + "" + line

    texto_primermensaje = texto_primermensaje.replace("'","")
    texto_primermensaje = texto_primermensaje.replace('\"','')
    return(texto_primermensaje)


'''****************************************************************************************************
* Description: split the text given as individual tokens
* INPUT: rawtext to split
* OUTPUT: list of tokens
****************************************************************************************************'''

def tokenize(rawtext):
    """ Split the text given as tokens.

    Args:
        rawtext(str): the text that should be splitted.

    Returns:
        A list with the tokens.

    """
    soup = BeautifulSoup(rawtext,"lxml")

    text = soup.get_text(strip=True)

    tokens = [t for t in text.split()]

    for pos, token in enumerate(tokens):
        tokens[pos] = token.translate({ord(i): None for i in '.,:()[]{}·0123456789/*-+<>'}) #characters that should not appear in a token

    clean_tokens = tokens[:]

    sr = stopwords.words('spanish') #by now only in spanish content #TO DO languaje detector + adaptation
    for token in tokens:
        if token in sr:
            clean_tokens.remove(token)
        if token == "":
            clean_tokens.remove(token)

    return(clean_tokens)


def lemmatize(tokens): #currently not used by the API
    """ Apply lemmatize rules to extract the root of any token given.

    Args:
        tokens(list of str): the list of tokens to lemmatize.

    Returns:
        A list with the tokens lemmatized.

    """
    stemmer = SnowballStemmer('spanish') #by now only in spanish content #TO DO languaje detector + adaptation

    for posicion, token in enumerate(tokens):
        tokens[posicion] = stemmer.stem(token)
    return(tokens)




def counter(tokens): #currently not used by the API
    """ Count the tokens of a given list.

    Args:
        tokens(list of str): the list of tokens to count.

    Returns:
        An ordered dict with pairs token - number of occurences.

    """
    freq = nltk.FreqDist(tokens)
    dd = OrderedDict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    return(dd)




def isPhishing(listURLS):
    """Function to check if the URLs detected at a mail are reflected at our phishing URLs.

    Args:
        listURLS (list[string]): List of URLs to analyze.

    Returns:
        0 if none of the URLs are considered phishing.
        1 if any of the URLs are at our phishing database.

    Raises:
      mySqlException: an error occured accessing the database.
    """

    listPhishing = []
    try:
        conexion = cn.dbConnectMySQL()
        mycursor = conexion.cursor()

       # Using the cursor as iterator
        mycursor.execute("SELECT site_url FROM phishing WHERE date_added >= NOW() - INTERVAL 60 DAY")
        for row in mycursor:
            listPhishing.insert(0,str(row[0]))

        conexion.commit()

    except cn.mySqlException as e:
        raise e
    finally:
        try:
            if conexion is not None:
                conexion.close()
        except cn.mySqlException as eCon:
            raise eCon

    if(not listURLS):
        return(0)


    found = 0
    for url in listURLS:
        for urlPhish in listPhishing:
            urlPhish = urlPhish.split("/")[2]
            found = re.search(urlPhish, url)
            if (found):
                break
        if (found):
            break
    if (found == None):
        foundPhish = 0
    else:
        foundPhish = 1

    return(foundPhish)




def selectDpt(text):
    """Function to  classify the given text as one of the predefined departments (by the machine learning model).

    Args:
        text(str): Text to classify.

    Returns:
        The name of the expected department.
    """

    with open('./modeloEmailClassification/text_classifier', 'rb') as training_model:
        model = pickle.load(training_model)

    with open('./modeloEmailClassification/documents', 'rb') as documents_model:
        documents = pickle.load(documents_model)


    #turn text into numbers and compose Bag of words
    sr = stopwords.words('spanish')
    customstopwords = ["ab", "agradecería", "ahora", "alguna", "alguno", "algún", "arsys", "asi", "asunto", "así", "ayer", "ayuda", "buenos", "cada", "cm", "com", "content", "continuación", "cualquier", "después", "do", "días", "estimado", "etc", "favor", "for", "fra", "fri", "gracias", "hola", "img", "jan", "miércoles", "nurialorenzoc", "of", "ra", "rsa", "saludo", "si", "tambien", "tardes", "the", "to", "va", "viernes"]
    for word in customstopwords:
        sr.insert(0,word)
    vectorizer = CountVectorizer(max_features=1500, min_df=3, max_df=0.7, stop_words=sr)
    X = vectorizer.fit_transform(documents).toarray()


    #Finding TFIDF
    tfidfconverter = TfidfTransformer()
    X = tfidfconverter.fit_transform(X).toarray()


    #predict the new text
    text = vectorizer.transform([text]).toarray()
    text = tfidfconverter.transform(text).toarray()
    modelPrediction = model.predict_proba(text)[0]


    probSoporte = round(modelPrediction[0]*100,2)
    probTramites = round(modelPrediction[1]*100,2)

    pred = Prediction()
    if(abs(probSoporte-probTramites)<20):
        pred.setDpto("Could not be determined")
        pred.setProb(max(probSoporte,probTramites))
    elif(probSoporte>probTramites):
        pred.setDpto("Soporte")
        pred.setProb(probSoporte)
    else:
        pred.setDpto("Tramites")
        pred.setProb(probTramites)

    return(pred)
