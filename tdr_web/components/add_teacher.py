import reflex as rx
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.navbar import navbar
from db.db_client import db


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

def add_teacher() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading('Afegir alumnes', size="7",align='center',padding='1em', color=colors.VERD.value),
                rx.text("Posa el correu del professor"),
                chakra_input(
                    placeholder="Ex: ecubi@ie-josepmxandri.cat",
                    on_change=AddTeacher.send_teacher_mail
                ),
                rx.text("Posa la contrassenya de l'usuari"),
                chakra_input(
                    placeholder="Ex: ecubi0123",
                    on_change=AddTeacher.send_teacher_password,
                ),
                rx.text("Tipus d'accés"),
                rx.select(
                    ['Administrador',"Usuari bàsic"],
                    width='100%',
                    on_change=AddTeacher.send_autoritzat,
                ),
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
    

class AddTeacher(rx.State):
    teacher_mail:str = ''
    teacher_password:str = ''
    autoritzacio:str = ''
    autoritzat:bool = False
    
    
    @rx.event
    def send_teacher_mail(self,mail):
        self.teacher_mail = mail
    
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
        
    def add_user(self):
        dbprofes = db["professor"]
        alumne = dbprofes.find_one({"Correu":self.teacher_mail})
        try:
            if not alumne:
                dbprofes.insert_one({
                    "Correu": self.teacher_mail,
                    "Contrassenya": self.teacher_password,
                    "Autoritzat": self.autoritzat
                }),
                return rx.toast.success('Professor afegit corractement')
            if alumne:
                return rx.toast.error("Aquest usuari ja existeix")
        except Exception as e:
            return rx.toast.error(e)
        
