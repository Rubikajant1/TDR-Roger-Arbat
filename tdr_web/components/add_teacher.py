### Add teacher ###
#Fitxer per afegir usuaris (professors)

#Importacions
import reflex as rx
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.navbar import navbar
from db.db_client import db


#Base de dades per als professors
dbprofes = db["professor"]

#Funció que crea un input amb els parametres estètics
def chakra_input(placeholder,on_change) -> rx.Component:
    return rx.input(
        placeholder=placeholder,
        on_change=on_change,
        width="300px",
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


#Funció front-end per afegir usuaris
def add_teacher() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                #Títol
                rx.heading('Afegir alumnes', size="7",align='center',padding='1em', color=colors.VERD.value),
                rx.text('Posa el nom'),
                chakra_input(
                    placeholder='Ex: Ester Cubí',
                    on_change=AddTeacher.send_teacher_name
                ),
                rx.text("Posa el correu del professor"),
                #Input per posar el correu de l'usuari
                chakra_input(
                    placeholder="Ex: ecubi@ie-josepmxandri.cat",
                    on_change=AddTeacher.send_teacher_mail
                ),
                rx.text("Posa la contrassenya de l'usuari"),
                #Input per posar la contrassenya
                chakra_input(
                    placeholder="Ex: ecubi0123",
                    on_change=AddTeacher.send_teacher_password,
                ),
                rx.text("Tipus d'accés"),
                #Seleccionar tipus d'accés
                rx.select(
                    ['Administrador',"Usuari bàsic"],
                    width='100%',
                    on_change=AddTeacher.send_autoritzat,
                ),
                #Botó final per afegir l'usuari
                rx.button(
                    "Afegir usuari",
                    background_color=colors.PRIMARY.value,
                    on_click=AddTeacher.add_user()
                ),
                align='center'
            ),
            padding='4em'
        )
    )
    
#Funció back-end per afegir usuari
class AddTeacher(rx.State):
    teacher_name:str =''
    teacher_mail:str = ''
    teacher_password:str = ''
    autoritzacio:str = ''
    autoritzat:bool = False
    
    #Funcions per passar del que es posa a l'input a la variable de la classe
    @rx.event
    def send_teacher_mail(self,mail):
        self.teacher_mail = mail
    
    @rx.event
    def send_teacher_name(self, new_name):
        self.teacher_name = new_name
    
    @rx.event
    def send_teacher_password(self, password):
        self.teacher_password = password
        
    @rx.event
    def send_autoritzat(self,autoritzacio):
        self.autoritzacio = autoritzacio
        if self.autoritzacio == "Administrador":
            self.autoritzat = True
        else:
            self.autoritzat = False
        
    #Funció per afegir l'usuai
    def add_user(self):
        #Variable on es busca un profe amb el mateix correu
        profe = dbprofes.find_one({"Correu":self.teacher_mail})
        try:
            if not profe:
                #Si no hi ha cap professor amb aquest correu s'inserta el profe amb els parametres anteriors
                dbprofes.insert_one({
                    "Nom":self.teacher_name,
                    "Correu": self.teacher_mail,
                    "Contrassenya": self.teacher_password,
                    "Autoritzat": self.autoritzat
                }),
                #Retornar un toast dient que ha sigut afegit correctament
                return rx.toast.success('Professor afegit corractement')
            if profe:
                #Si ja hi ha algún usuari amb aquest correu es retorna un toast que indica que aquest usuari ja existeix i no s'inserta cap més
                return rx.toast.error("Aquest usuari ja existeix")
        except Exception as e:
            return rx.toast.error(e)
        
