### Tdr web ###
# Pàgina principal 

#importacions
import reflex as rx
import hashlib
from tdr_web.components.navbar import navbar
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.header import header
from tdr_web.styles.styles import BASE_STYLE
from tdr_web.components.primer import primer, AlumneState1r
from tdr_web.components.segon import segon, AlumneState2n
from tdr_web.components.tercer import tercer, AlumneState3r
from tdr_web.components.quart import quart, AlumneState4t
from tdr_web.components.add_students import afegir_alumnes
from tdr_web.components.modify_student import modificar_alumne, AlumnState
from tdr_web.components.add_teacher import add_teacher
from tdr_web.components.modify_teacher import modificar_usuaris, TeacherState
from db.db_client import db


#configuració de la web
config = rx.Config(
    app_name='Web TDR',
    frontend_port=3000,
)


#Class per verificar l'usuari
class Verify(rx.State):
    is_authenticated: bool = False
    password_input: str = ""
    user_input:str = ""
    show_error: bool = False
    user:dict = {}


    #Funcions que passen els inputs a variables de la classe
    @rx.event
    def send_password_input(self,pasword):
        self.password_input = pasword

    @rx.event
    def send_user_input(self,user):
        self.user_input = user
    
    #Revisar usuari
    def check_user(self):
        try:
            #Obtenir la base de dades de professors i crear una variable
            dbprofe = db['professor']
            #Variable usuari que busca un usuari amb el mateix correu que s'ha posat
            usuari = dbprofe.find_one({"Correu":self.user_input})
            #Es passa l'input de la contrassenya a xifrat
            hashed_password_input = hashlib.sha256(self.password_input.encode()).hexdigest()
            hashed_correct = hashlib.sha256(usuari["Contrassenya"].encode()).hexdigest()
            #Si s'ha trobat un usuari amb el correu
            if usuari:
                # Verificar si la contrassenya posada coincideix amb la contrassenya real de l'usuari
                if hashed_password_input == hashed_correct:
                    #Canviar les variables indicant que està verificat i no hi ha cap error
                    self.is_authenticated = True
                    self.show_error = False
                    self.user = usuari
                else:
                    #Si no és correcte posar que no está verificat i que es mostri l'error
                    self.is_authenticated = False
                    self.show_error = True
                    self.password_input = ""
        #En cas de que l'usuari no sigui correcte es mostra un toast
        except:
                return rx.toast.error("No hi ha cap usuari amb aquest correu")
                
    
    #Funció per tancar sessió
    def logout(self):
        self.user_input = ""
        self.password_input = ""
        self.is_authenticated = False
        return rx.redirect("/") 
    


#Front-end de la pagina d'inici de sessió
def login_page() -> rx.Component:
    return rx.box(
        rx.box(
            #Navbar personalitzada per l'accés restringit
            rx.flex(
                rx.text("Gestió d'estudiants de l'IE Josep Maria Xandri",color='white',size='4'),
                rx.text("By Roger Arbat Juventeny",color='white'),
                position = 'fixed',
                bg = colors.PRIMARY.value,
                width = '100%',
                padding_x = '16px',
                padding_y = '8px',
                z_index = '100% !important',
                spacing='9',
                justify='between'
            )
        ),
        rx.vstack(
            #Icone del candau tancat que indica que l'accés està restringit
            rx.icon('lock-keyhole',color = colors.VERD.value,size=40),
            #Títol que ho torna a indicar
            rx.heading("Accés restringit", size="7",color=colors.VERD.value),
            rx.text("Entra el teu usuari"),
            #Input que recull el correu de l'usuari
            rx.input(
                placeholder="correu de l'usuari",
                value=Verify.user_input,
                on_change=Verify.send_user_input,
                width='400px'
            ),
            #Input de la contrassenya
            rx.input(
                placeholder="contrassenya",
                value=Verify.password_input,
                on_change=Verify.send_password_input,
                type="password",
                width='400px'
            ),
            #Botó que crida la funció que verifica si está correctament autenticat
            rx.button(
                "Entrar", 
                on_click=Verify.check_user,
                color_scheme="blue",
                width = '400px',
                height = "30px",
                background_color = colors.PRIMARY.value
            ),
            #Si la contrassenya no és correcte es mostra un text de color vermell
            rx.cond(
                Verify.show_error,
                rx.text("Contraseña incorrecta", color="red")
            ),
            spacing="4",
            align="center",
            height="100vh",
            justify="center"
        ),
    )


#Front-end de la pàgina principal un cop registrat   
def protected_content() -> rx.Component:
    return rx.box(
        #Cridar la funció navbar a la part superior
        navbar(),
        rx.center(
            rx.vstack(
                #Cridar la funció header a sota
                header(),
                max_width='600px',
                width='100%',
                height = '100vh',
                margin='1em'
            ),
            margin_bottom='14em'
        ),
        spacing="4"
    )

# Funció que decideix quina pàgina mostrar segons si s'ha registrat correctament
def index() -> rx.Component:
    return rx.cond(
        Verify.is_authenticated,
        #si està autenticat es mostra el contingut normal (o "protegit")
        protected_content(),
        #Si no está autenticat es mostra la pàgina d'inici
        login_page()
    )

#Crear la app
app = rx.App(
        style=BASE_STYLE
    )

#Afegir la pàgina principal
app.add_page(
    index, #Funció front-end que es crida al accedir a la página
    title='Web TDR',
    route='/',#Ruta on està colocada la pàgina
    description="Gestió d'estudiants i d'assistencia de l'IE Josep Maria Xandri",
),

#Afegir altres pàgines
app.add_page(primer,route='/primer', title='Primer', on_load=AlumneState1r.initial_load)
app.add_page(segon,route='/segon', title='Segon', on_load=AlumneState2n.initial_load)
app.add_page(tercer,route='/tercer', title='Tercer', on_load=AlumneState3r.initial_load)
app.add_page(quart,route='/quart', title='Quart', on_load=AlumneState4t.initial_load)
app.add_page(afegir_alumnes,route='/add_student',title='Afegir alumnes')
app.add_page(modificar_alumne,route='/modify_student',title='Modificar alumnes',on_load=AlumnState.load_alumnes)
app.add_page(add_teacher,route='/add_teacher',title="Afegir professor")
app.add_page(modificar_usuaris,route="/modify_users",title="Modificar usuaris",on_load=TeacherState.load_teachers)