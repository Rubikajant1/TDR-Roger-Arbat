### Add students ###
#Fitxer per afegir alumnes

#Importacions
import reflex as rx
from tdr_web.components.navbar import navbar
from tdr_web.styles.colors import Colors as colors
from db.db_client import db

#Obtenir la base de dades per als alumnes
dbalumnes = db['alumnes']

#Funció que crea un input amb els parametres estètics
def chakra_input(placeholder,on_change) -> rx.Component:
    return rx.input(
        placeholder=placeholder,
        on_change=on_change,
        width="100%",
        px="4",
        py="2",
        border="1px solid",
        border_color="gray.200",
        border_radius="md",
        bg="white",
        font_size="md",
        color="gray.800",
        _placeholder={"color": "gray.400"},
        _hover={
            "border_color": "blue.500",
        },
        _focus={
            "border_color": "blue.500",
            "box_shadow": "0 0 0 1px #3182ce",
            "outline": "none"
        },
        _invalid={
            "border_color": "red.500",
            "_hover": {"border_color": "red.600"},
            "_focus": {
                "border_color": "red.500",
                "box_shadow": "0 0 0 1px #E53E3E"
            }
        }
    ),

# Funció front-end per afegir alumnes
def afegir_alumnes() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                #Títol
                rx.heading('Afegir alumnes', size="7",align='center',padding='1em', color=colors.VERD.value),
                rx.text("Nom i els cognoms de l'alumne"),
                #Input per al nom del alumne
                chakra_input(
                    placeholder="Ex: Roger Arbat Juventeny",
                    on_change=AddStudents.change_name
                ),
                rx.text("Correu de l'alumne"),
                #Input pel correu de l'alumne
                chakra_input(
                    placeholder="Ex: roger.arbat@ie-josepmxandri.cat",
                    on_change=AddStudents.change_correu_alumne
                ),
                rx.text("Correu d'un familiar"),
                #Input pel correu del familiar
                chakra_input(
                    placeholder="Ex: pares_alumne@gmail.com",
                    on_change=AddStudents.change_correu_familia
                ),
                rx.text("Correu del tutor"),
                #Input pel correu actual del tutor
                chakra_input(
                    placeholder="Ex: ecubi@ie-josepmxandri.cat",
                    on_change=AddStudents.change_correu_tutor
                ),
                rx.text('Curs'),
                #Select per a alguna de les 4 opcions
                rx.select(
                    ['1r ESO','2n ESO','3r ESO','4t ESO'],
                    value=AddStudents.select_value,
                    on_change=AddStudents.change_value,
                    width='300px'
                ),
                #Botó per guardar i insertar l'alumne a la base de dades
                rx.button(
                    'Guardar',
                    width='300px',
                    background_color=colors.PRIMARY.value,
                    on_click=AddStudents.add_student()
                ),
                align='center'
            ),
            padding='4em'
        )
    )
    
    
    
#Classe back-end on es processen les dades dels inputs i s'insereix un alumne
class AddStudents(rx.State):
    select_value:str = '1r ESO'
    nom:str = ''
    correu_alumne:str = ''
    correu_familia:str = ''
    correu_tutor:str = ''
    
    
    #Totes les funcions per passar els parametres dels inputs a les variables de les classes
    @rx.event
    def change_value(self, new_value):
        self.select_value = new_value
        
    @rx.event
    def change_name(self, new_name):
        self.nom = new_name
        
    @rx.event
    def change_correu_alumne(self, new_mail):
        self.correu_alumne = new_mail
        
    @rx.event
    def change_correu_familia(self, new_mail):
        self.correu_familia = new_mail
        
    @rx.event
    def change_correu_tutor(self, new_mail):
        self.correu_tutor = new_mail
    
    
    #Funció per afegir l'estudiant (cridada per el botó anterior) 
    def add_student(self):
        #Crear variable alumne que és una busqueda per el nom
        alumne = dbalumnes.find_one({"Nom":self.nom})
        try:
            if not alumne:
                #Si no hi ha cap alumne amb aquest nom, es pot insertar
                #Insersar alumne a la base de dades
                dbalumnes.insert_one({
                    'Nom': self.nom,
                    "Correu alumne": self.correu_alumne,
                    'Curs': self.select_value,
                    'Retards': 0,
                    'Faltes justificades': 0,
                    'Faltes no justificades': 0,
                    'Correu familiar': self.correu_familia,
                    'Correu del tutor': self.correu_tutor,
                    'Llista de retards': [],
                    'Llista de faltes justificades':[],
                    'Llista de faltes no justificades': []
                }),
                #Returnar que s'ha afegit l'alumne
                return rx.toast.success('Alumne afegit corractement')
            if alumne:
                #Si ja hi ha algun alumne amb aquest nom s'indica que no es pot insertar ja que ja hi ha un alumne amb aquest mateix nom
                #D'aquesta manera s'eviten alumnes repetits
                return rx.toast.error("Ja hi ha un alumne amb aquest nom")
        except Exception as e:
            return rx.toast.error(e)
        