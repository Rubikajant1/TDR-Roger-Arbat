### Modify teacher ###
#

#Importacions
import reflex as rx
import dataclasses
from tdr_web.components.navbar import navbar
from db.db_client import db
from tdr_web.styles.colors import Colors as colors
from reflex_ag_grid import ag_grid
from typing import List


#Cridar la base de dades dels professors
dbprofes = db['professor']


#Classe back-end per a modificar els professors
class TeacherState(rx.State):
    #Variables de la classe
    teacher_list: list = []
    selected_teacher_ids: list[str] = []
    search_text: str = ""
    sort_value: str = ""
    pts:int = 0
    tutor:bool = False

    #Funció per al load inicial
    def load_teachers(self):
        #Passar l'id del profe de ObjectId a str
        raw_teacher = [
            {**teacher, '_id': str(teacher['_id'])}
            for teacher in dbprofes.find({})
        ]
        self.teacher_list =[
            {
                **teacher,
                "Autoritzat": teacher.get("Autoritzat"),
                "auth": "Administrador" if teacher.get("Autoritzat") == True else "Usuari bàsic"
            }
            # Cicle for per a cada alumne de la variable row alumnes creada anteriorment
            for teacher in raw_teacher
        ]


    #Funció pel buscador
    @rx.var(cache=True)
    def filtered_teachers(self) -> list:
        teachers = self.teacher_list

        if self.sort_value:
            teachers = sorted(
                teachers,
                key=lambda x: str(x.get(self.sort_value, "")).lower()
            )

        # Aplicar búsqueda 
        if self.search_text:
            search_lower = self.search_text.lower()
            teachers = [
                teacher for teacher in teachers
                if any(
                    search_lower in str(value).lower()
                    for value in teacher.values()
                )
            ]
        
        return teachers

    #Funcions que canvien els parametres
    @rx.event
    def handle_selection_changed(self, selected_rows: List[dict]):
        self.selected_teacher_ids = [str(row['Nom']) for row in selected_rows]

        
    @rx.event
    def set_sort_value(self, value: str):
        self.sort_value = value

    @rx.event
    def set_search_text(self, value: str):
        self.search_text = value
        
    #Funció per eliminar algún usuari
    def delete_teacher(self):
        try:
            for teacher_name in self.selected_teacher_ids:
                dbprofes.delete_one({'Nom':teacher_name})
                return rx.toast.success(f"{teacher_name} eliminat correctament")
        except Exception as e:
            return rx.toast.error(e)
    
    #Funció per modificar l'accés d'un usuari
    def modify_acces(self):
        try:
            #Per cada alumne seleccionat
            for teacher_name in self.selected_teacher_ids:
                #Crear una variable amb l'usuari
                user = dbprofes.find_one({"Nom":teacher_name})
                #Si está autorizat
                if user["Autoritzat"] == True:
                    #Actualitzar l'usuari a no autoritzat
                    dbprofes.update_one(
                       {"Nom": teacher_name},
                       {"$set": {"Autoritzat":False}}
                    )
                    #Mostrar-ho
                    return rx.toast.success("Usuari canviat d'accés correctament")
                #Si no està autoritzat
                if user["Autoritzat"]==False:
                    #Actualitzar-lo a autoritzat
                    dbprofes.update_one(
                       {"Nom": teacher_name},
                       {"$set": {"Autoritzat":True}}
                    )
                    #Mostrar-ho
                    return rx.toast.success("Usuari canviat d'accés correctament")
        except Exception as e:
            print(e)
            return rx.toast.error(e)
    
    
#Columnes de la taula
column_defs = [
    ag_grid.column_def(
        align='center',
        field="selected", 
        header_name="", 
        checkboxSelection=True,
        headerCheckboxSelection=True,
        width='55px'
    ),
    ag_grid.column_def(
        field="Correu", 
        header_name="Correu",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width='570px',
        sortable=True,
    ),
    ag_grid.column_def(
        field="auth",
        header_name="Autorització",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width='570px',
        sortable=True
    )
]

#Funció front-end per al modificador d'usuaris
def modificar_usuaris() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                #Títol
                rx.heading("Modificar usuaris", color=colors.VERD.value),
                #Input que fa de buscador d'usuaris
                rx.input(
                    placeholder="Buscar usuari",
                    on_change=TeacherState.set_search_text,
                    width="70%",
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
                #Taula amb les columnes anteriors
                ag_grid(
                    id="usuaris_grid",
                    column_defs=column_defs,
                    row_data=TeacherState.filtered_teachers,
                    width="1200px",
                    height="45vh",
                    row_selection="multiple",
                    on_selection_changed=TeacherState.handle_selection_changed,
                ),
                #Botons per modificar
                rx.hstack(
                    rx.button(
                        "Eliminar Usuari",
                        background_color = colors.PRIMARY.value,
                        on_click=TeacherState.delete_teacher,
                        width = '243px'
                    ),
                    rx.button(
                        "Modificar acces",
                        background_color=colors.PRIMARY.value,
                        on_click=TeacherState.modify_acces,
                        width = '200px'
                    ),
                    spacing="3",
                    align='center'
                ),
                align="center"
            ),
            width="100%",
            padding="8em",
        ),
    )