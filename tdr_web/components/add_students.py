import reflex as rx
from tdr_web.components.navbar import navbar
from tdr_web.styles.colors import Colors as colors
from db.db_client import db

# Obtener la colección (importante!)
dbalumnes = db['alumnes']

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


def afegir_alumnes() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading('Afegir alumnes', size="7",align='center',padding='1em', color=colors.VERD.value),
                rx.text("Nom i els cognoms de l'alumne"),
                chakra_input(
                    placeholder="Ex: Roger Arbat Juventeny",
                    on_change=AddStudents.change_name
                ),
                rx.text("Correu de l'alumne"),
                chakra_input(
                    placeholder="Ex: roger.arbat@ie-josepmxandri.cat",
                    on_change=AddStudents.change_correu_alumne
                ),
                rx.text("Correu d'un familiar"),
                chakra_input(
                    placeholder="Ex: pares_alumne@gmail.com",
                    on_change=AddStudents.change_correu_familia
                ),
                rx.text("Correu del tutor"),
                chakra_input(
                    placeholder="Ex: ecubi@ie-josepmxandri.cat",
                    on_change=AddStudents.change_correu_tutor
                ),
                rx.text('Curs'),
                rx.select(
                    ['1r ESO','2n ESO','3r ESO','4t ESO'],
                    value=AddStudents.select_value,
                    on_change=AddStudents.change_value,
                    width='300px'
                ),
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
    
    
    
    
class AddStudents(rx.State):
    select_value:str = '1r ESO'
    nom:str = ''
    correu_alumne:str = ''
    correu_familia:str = ''
    correu_tutor:str = ''
    
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
        
    def add_student(self):
        alumne = dbalumnes.find_one({"Nom":self.nom})
        try:
            if not alumne:
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
                return rx.toast.success('Alumne afegit corractement')
            if alumne:
                return rx.toast.error("Ja hi ha un alumne amb aquest nom")
        except Exception as e:
            return rx.toast.error(e)