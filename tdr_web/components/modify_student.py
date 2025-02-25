import reflex as rx
import dataclasses
from tdr_web.components.navbar import navbar
from db.db_client import db_client
from tdr_web.styles.colors import Colors as colors
from reflex_ag_grid import ag_grid
from typing import List

db = db_client['alumnes']
dbalumnes = db['alumnes']

@dataclasses.dataclass
class Alumne:
    nom: str
    curs: str
    correu_tutor: str
    
class AlumnState(rx.State):
    alumn_list: list = []
    selected_alumne_ids: list[str] = []
    search_text: str = ""
    sort_value: str = ""
    pts:int = 0
    tutor:bool = False
    new_tutor:str
    new_mail:str
    
    def send_new_tutor(self,nwmail):
        self.new_mail = nwmail
    
    def send_new_tutor(self,nou_tutor):
        self.new_tutor = nou_tutor
    
    def tutor_show(self):
        self.pts+=1
        if self.pts%2==0:
            self.tutor = True
        else:
            self.tutor = False
    
    def load_alumnes(self):
        raw_alumnes = [
            {**alumne, '_id': str(alumne['_id'])}
            for alumne in dbalumnes.find({})
        ]
        self.alumn_list = raw_alumnes

    @rx.var(cache=True)
    def filtered_alumnes(self) -> list:
        alumnes = self.alumn_list

        # Aplicar ordenamiento si hay un valor de ordenamiento
        if self.sort_value:
            alumnes = sorted(
                alumnes,
                key=lambda x: str(x.get(self.sort_value, "")).lower()
            )

        # Aplicar búsqueda si hay texto de búsqueda
        if self.search_text:
            search_lower = self.search_text.lower()
            alumnes = [
                alumne for alumne in alumnes
                if any(
                    search_lower in str(value).lower()
                    for value in alumne.values()
                )
            ]
        
        return alumnes

    @rx.event
    def handle_selection_changed(self, selected_rows: List[dict]):
        self.selected_alumne_ids = [str(row['Nom']) for row in selected_rows]

        
    @rx.event
    def set_sort_value(self, value: str):
        self.sort_value = value

    @rx.event
    def set_search_text(self, value: str):
        self.search_text = value

    def tutor_change(self):
        if self.selected_alumne_ids:
            try:
                for alumne_nom in self.selected_alumne_ids:
                    dbalumnes.update_one(
                        {"Nom": alumne_nom},
                        {"$set": {"Correu del tutor": self.new_mail}}
                    )
                return rx.toast.success("Correus actualitzats correctament")
            except Exception as e:
                return rx.toast.error(str(e))
        else:
            return rx.toast.error("No hi ha cap alumne seleccionat")
        
    def familly_change(self):
        if self.selected_alumne_ids:
            try:
                for alumne_nom in self.selected_alumne_ids:
                    dbalumnes.update_one(
                        {"Nom": alumne_nom},
                        {"$set": {"Correu familiar": self.new_mail}}
                    )
                return rx.toast.success("Correus actualitzats correctament")
            except Exception as e:
                return rx.toast.error(str(e))
        else:
            return rx.toast.error("No hi ha cap alumne seleccionat")
        
    
    def delete_student(self):
        try:
            for alumne_nom in self.selected_alumne_ids:
                dbalumnes.delete_one({'Nom':alumne_nom})
                return rx.toast.success(f"{alumne_nom} eliminat correctament")
        except Exception as e:
            return rx.toast.error(e)

    def retrocedir_curs(self):
        if self.selected_alumne_ids:
            try:
                for alumne_id in self.selected_alumne_ids:
                    alumne = dbalumnes.find_one({"Nom": alumne_id})
                    if alumne["Curs"] == '1r ESO':
                        return rx.toast.error("No es pot retrocedir un alumne de 1r d'ESO")
                    else:
                        if alumne["Curs"]=='2n ESO':
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '1r ESO'}}
                            )
                            return rx.toast.success(f"{alumne["Nom"]} de 2n d'ESO passat a 1r d'ESO")
                        if alumne["Curs"] == '3r ESO':
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '2n ESO'}}
                            )
                            return rx.toast.success(f"{alumne["Nom"]} de 3r d'ESO passat a 2n d'ESO")
                        if alumne["Curs"]=='4t ESO':
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '3r ESO'}}
                            )
                            return rx.toast.success(f"{alumne["Nom"]} de 4t d'ESO passat a 3r d'ESO")
            except Exception as e:
                self.selected_alumne_ids = []
                return rx.toast.error(e)
        else:
            self.selected_alumne_ids = []
            return rx.toast.error("No hi ha cap alumne seleccionat")
        self.selected_alumne_ids = []
    
    
    def avançar_curs(self):
        if self.selected_alumne_ids:
            try:
                for alumne_id in self.selected_alumne_ids:
                    alumne = dbalumnes.find_one({"Nom": alumne_id})
                    if alumne["Curs"] == '4t ESO':
                        return rx.toast.error("No es pot avançar un alumne de 4t d'ESO")
                    else:
                        if alumne["Curs"]=='3r ESO':
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '4t ESO'}}
                            )
                            return rx.toast.success(f"{alumne["Nom"]} de 3r d'ESO passat a 4t d'ESO")
                        if alumne["Curs"] == '1r ESO':
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '2n ESO'}}
                            )
                            return rx.toast.success(f"{alumne["Nom"]} de 1r d'ESO passat a 2n d'ESO")
                        if alumne["Curs"]=='2n ESO':
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '3r ESO'}}
                            )
                            return rx.toast.success(f"{alumne["Nom"]} de 2n d'ESO passat a 3r d'ESO")
            except Exception as e:
                self.selected_alumne_ids = []
                return rx.toast.error(e)
        else:
            self.selected_alumne_ids = []
            return rx.toast.error("No hi ha cap alumne seleccionat")
        self.selected_alumne_ids = []

column_defs = [
    ag_grid.column_def(
        align='center',
        field="selected", 
        header_name="", 
        checkboxSelection=True,
        headerCheckboxSelection=True,
        width='50%'
    ),
    ag_grid.column_def(
        field="Nom",
        header_name="Nom",
        width='400%',
        sortable=True
    ),
    ag_grid.column_def(
        field="Curs", 
        header_name="Curs",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width='120%',
        sortable=True
    ),
    ag_grid.column_def(
        field="Correu del tutor", 
        header_name="Correu del tutor",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width='308%',
        sortable=True
    ),
    ag_grid.column_def(
        field="Correu familiar",
        header_name="Correu familiar",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width='308',
        sortable=True
    )
]

def modificar_alumne() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Modificar alumnes", color=colors.VERD.value),
                rx.input(
                    placeholder="Buscar alumne, curs o correus",
                    on_change=AlumnState.set_search_text,
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
                ag_grid(
                    id="alumnes_grid",
                    column_defs=column_defs,
                    row_data=AlumnState.filtered_alumnes,
                    width="1200px",
                    height="45vh",
                    row_selection="multiple",
                    on_selection_changed=AlumnState.handle_selection_changed,
                ),
                rx.input(
                    placeholder="Posa el nou correu",
                    on_change=AlumnState.set_new_mail,
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
                rx.hstack(
                    rx.button(
                        "Eliminar Alumne",
                        background_color = colors.PRIMARY.value,
                        on_click=AlumnState.delete_student,
                        width = '243px'
                    ),rx.button(
                        "Canviar el correu del tutor",
                        background_color=colors.PRIMARY.value,
                        on_click=AlumnState.tutor_change,
                        width = '243px'
                    ),
                    rx.button(
                        "Canviar el correu familiar",
                        background_color = colors.PRIMARY.value,
                        on_click=AlumnState.familly_change,
                        width = '243px'
                    ),
                    rx.button(
                        "Retrocedir un curs",
                        background_color=colors.PRIMARY.value,
                        on_click=AlumnState.retrocedir_curs,
                        width = '200px'
                    ),
                    rx.button(
                        "Avançar un curs",
                        background_color=colors.PRIMARY.value,
                        on_click=AlumnState.avançar_curs,
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