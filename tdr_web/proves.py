from pymongo import MongoClient

db_client=MongoClient('mongodb+srv://tdrarbat:arbat0123@cluster0.j76iw.mongodb.net/')

db = db_client['Escola']
dbprofe = db['professor']

usuari:dict = {
    "Correu":"autoritzat@gmail.com",
    "Contrassenya":"autoritzat",
    "Autoritzat":True
}

dbprofe.insert_one(usuari)