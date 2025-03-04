from pymongo import MongoClient

db_client=MongoClient('mongodb+srv://tdrarbat:arbat0123@cluster0.j76iw.mongodb.net/')

db = db_client['Escola']
dbprofe = db['professor']

usuari:dict = {
    "Correu":"noautoritzat@gmail.com",
    "Contrassenya":"noautoritzat",
    "Autoritzat":False
}

dbprofe.insert_one(usuari)