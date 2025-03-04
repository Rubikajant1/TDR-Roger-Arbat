import reflex as rx
from tdr_web.components.navbar import navbar
from db.db_client import db
from tdr_web.styles.colors import Colors as colors

def chakra_input(placeholder,on_change,on_click) -> rx.Component:
    return rx.input(
        placeholder=placeholder,
        on_change=on_change,
        on_click=on_click,
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


# Obtener la colección (importante!)
dbalumnes = db['alumnes']


class AlumnState(rx.State):
    alumn_list:list = []
    alumne:str
    nom_alumne:str
    curs_alumne:str
    trobat:bool = False
    n_trobat:bool = False
    
    @rx.event
    def send_student(self,student_name):
        self.alumne = student_name
    
    def resetejar(self):
        self.trobat=False
        self.n_trobat=False
    
    def search_student(self):
        trobar = list(dbalumnes.find({"Nom": self.alumne}))
        if trobar:
            self.trobat = True
            self.n_trobat = False
            self.alumn_list = trobar
            self.nom_alumne= trobar[0]['Nom']
            self.curs_alumne = trobar[0]['Curs']
        else:
            self.trobat = False
            self.n_trobat = True
    
    
    def delete_student(self):
        try:
            dbalumnes.delete_one({'Nom':self.nom_alumne})
            return rx.toast.success(f"{self.nom_alumne} eliminat correctament")
        except Exception as e:
            print(e)
            return rx.toast.error(e)
    

def treure_alumnes() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Treure alumnes",color=colors.VERD.value),
                chakra_input(
                    placeholder="Busca algun alumne",
                    on_change=AlumnState.send_student,
                    on_click=AlumnState.resetejar,
                ),
                rx.button(
                    'Eliminar alumne',
                    width='300px',
                    background_color=colors.PRIMARY.value,
                    on_click=AlumnState.search_student()
                ),
                rx.cond(
                    AlumnState.trobat,
                    rx.text(f"Segur que vols eliminar a {AlumnState.nom_alumne} de {AlumnState.curs_alumne}?")
                ),
                rx.cond(
                    AlumnState.trobat,
                    rx.button(f'Eliminar {AlumnState.nom_alumne}',background_color=colors.PRIMARY.value, on_click=AlumnState.delete_student())
                ),
                rx.cond(
                    AlumnState.n_trobat,
                    rx.text("No s'ha trobat cap alumne amb aquest nom", color='red')
                ),
                align='center'
            ),
        padding='10em'
        ),
    )
    