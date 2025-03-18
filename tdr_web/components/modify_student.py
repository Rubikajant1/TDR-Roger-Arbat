### Link button ###
#Fitxer que serveix per modificar els alumnes (correu familiar, tutor, curs...)

#Importacions
import reflex as rx
import dataclasses
from tdr_web.components.navbar import navbar
from db.db_client import db
from tdr_web.styles.colors import Colors as colors
from reflex_ag_grid import ag_grid
from typing import List

#Cridar la base de dades dels alumnes
dbalumnes = db['alumnes']


#Creo una classe back-end on es modifiquen els alumnes   
class AlumnState(rx.State):
    #Variables de la classe
    alumn_list: list = []
    selected_alumne_ids: list[str] = []
    search_text: str = ""
    sort_value: str = ""
    pts:int = 0
    tutor:bool = False
    new_tutor:str
    new_mail:str
    
    #Funcions que passen dels inputs a les variables
    def send_new_tutor(self,new_mail):
        self.new_mail = new_mail
    
    def send_new_tutor(self,nou_tutor):
        self.new_tutor = nou_tutor
    
    #Load inicial que es crida al tdr_web.py en la part "on_load ="
    def load_alumnes(self):
        #Es passen totes les persones a la variable de la llista "alumn_list"
        raw_alumnes = [
            {**alumne, '_id': str(alumne['_id'])}
            for alumne in dbalumnes.find({})
        ]
        self.alumn_list = raw_alumnes

    #Funció per ordenar alumnes quan es fa servir el buscador
    @rx.var(cache=True)
    def filtered_alumnes(self) -> list:
        alumnes = self.alumn_list

        # Ordenar
        if self.sort_value:
            alumnes = sorted(
                alumnes,
                key=lambda x: str(x.get(self.sort_value, "")).lower()
            )

        # Aplicar el valor de la busqueda si es que n'hi ha
        if self.search_text:
            search_lower = self.search_text.lower()
            alumnes = [
                alumne for alumne in alumnes
                if any(
                    #Es busca tot en minuscula per evitar errors de majuscules i minuscules
                    search_lower in str(value).lower()
                    for value in alumne.values()
                )
            ]
        
        return alumnes

    #Més funcions que canvien variables
    @rx.event
    def handle_selection_changed(self, selected_rows: List[dict]):
        self.selected_alumne_ids = [str(row['Nom']) for row in selected_rows]

        
    @rx.event
    def set_sort_value(self, value: str):
        self.sort_value = value

    @rx.event
    def set_search_text(self, value: str):
        self.search_text = value

    #Funció per canviar el correu del tutor
    def tutor_change(self):
        #Si hi ha algún alumne seleccionat:
        if self.selected_alumne_ids:
            try:
                for alumne_nom in self.selected_alumne_ids:
                    #Per cada alumne seleccionat
                    #Actualitzar un alumne amb el correu del nou tutor
                    dbalumnes.update_one(
                        {"Nom": alumne_nom},
                        {"$set": {"Correu del tutor": self.new_mail}}
                    )
                    #Mostrar que s'ha actualitzat correctament
                return rx.toast.success("Correus actualitzats correctament")
            except Exception as e:
                return rx.toast.error(str(e))
        else:
            #Si no hi ha cap alumne seleccionat 
            #Mostrar-ho
            return rx.toast.error("No hi ha cap alumne seleccionat")
    
    #Funció per canviar el correu familiar
    def familly_change(self):
        #Si hi ha algún alumne seleccionat
        if self.selected_alumne_ids:
            try:
                for alumne_nom in self.selected_alumne_ids:
                    #Per cada alumne selecccionat
                    #Actualitzar el correu familiar amb el nou
                    dbalumnes.update_one(
                        {"Nom": alumne_nom},
                        {"$set": {"Correu familiar": self.new_mail}}
                    )
                #Mostrar que s'ha actualitzat correctament
                return rx.toast.success("Correus actualitzats correctament")
            except Exception as e:
                return rx.toast.error(str(e))
        else:
            #Si no hi ha cap alumne seleccionat mostrar-ho
            return rx.toast.error("No hi ha cap alumne seleccionat")
        
    #Funció per eliminar un alumne
    def delete_student(self):
        try:
            #Per cada alumne seleccionat:
            for alumne_nom in self.selected_alumne_ids:
                #Eliminar l'alumne buscat per el nom
                dbalumnes.delete_one({'Nom':alumne_nom})
                #Retornar a l'usuari que s'ha eliminat correctament
                return rx.toast.success(f"{alumne_nom} eliminat correctament")
        except Exception as e:
            return rx.toast.error(e)

    #Funció que retrocedeix un curs als alumnes
    def retrocedir_curs(self):
        #Si hi ha algún alumne seleccionat:
        if self.selected_alumne_ids:
            try:
                #Per cada alumne seleccionat:
                for alumne_id in self.selected_alumne_ids:
                    #Trobar l'alumne seleccionat a la base de dades
                    alumne = dbalumnes.find_one({"Nom": alumne_id})
                    #Si l'alumne és de 1r d'ESO mostrar que no es pot retrocedir el curs ja que aquest programa només està fet per secundària
                    if alumne["Curs"] == '1r ESO':
                        #Mostrar que no es pot retrocedir
                        return rx.toast.error("No es pot retrocedir un alumne de 1r d'ESO")
                    #Qualsevol altre curs
                    else:
                        #Si és de segon d'eso:
                        if alumne["Curs"]=='2n ESO':
                            #Actualitzar el curs de l'alumne a 1r d'ESO
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '1r ESO'}}
                            )
                            #Retornar que s'ha passat de curs correctament
                            return rx.toast.success(f"{alumne["Nom"]} de 2n d'ESO passat a 1r d'ESO")
                        #Si l'alumne és de 3r d'ESO
                        if alumne["Curs"] == '3r ESO':
                            #Actualitzar el curs a 2n d'ESO
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '2n ESO'}}
                            )
                            #Mostrar-ho
                            return rx.toast.success(f"{alumne["Nom"]} de 3r d'ESO passat a 2n d'ESO")
                        #Si l'alumne fa 4t d'ESO
                        if alumne["Curs"]=='4t ESO':
                            #Actualitzar el curs de l'alumne a 3r d'eso
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '3r ESO'}}
                            )
                            #Mostrar-ho
                            return rx.toast.success(f"{alumne["Nom"]} de 4t d'ESO passat a 3r d'ESO")
            except Exception as e:
                self.selected_alumne_ids = []
                return rx.toast.error(e)
        else:
            #Si no hi ha alumne no passa res i es mostra que no hi ha cap alumne seleccionat
            self.selected_alumne_ids = []
            return rx.toast.error("No hi ha cap alumne seleccionat")
        self.selected_alumne_ids = []
    
    
    #Funció per avançar un curs
    def avançar_curs(self):
        #Si hi ha algún alumne seleccionat
        if self.selected_alumne_ids:
            try:
                #Per cada alumne seleccionat:
                for alumne_id in self.selected_alumne_ids:
                    #Buscar l'alumne a la base de dades
                    alumne = dbalumnes.find_one({"Nom": alumne_id})
                    #Si l'alumne fa 4t d'ESO 
                    if alumne["Curs"] == '4t ESO':
                        #Retornar que no es pot avançar un alumne de 4t d'ESO ja que és el máxim que hi ha actualment
                        return rx.toast.error("No es pot avançar un alumne de 4t d'ESO")
                    #Si fa qualsevol altre curs
                    else:
                        #Si l'alumne fa 3r d'ESO
                        if alumne["Curs"]=='3r ESO':
                            #Actualitzar el curs a 4t d'ESO
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '4t ESO'}}
                            )
                            #Mostrar-ho
                            return rx.toast.success(f"{alumne["Nom"]} de 3r d'ESO passat a 4t d'ESO")
                        #Si fa 2n d'ESO 
                        if alumne["Curs"]=='2n ESO':
                            #Actualitzar-lo a 3r d'ESO
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '3r ESO'}}
                            )
                            #Mostrar-ho
                            return rx.toast.success(f"{alumne["Nom"]} de 2n d'ESO passat a 3r d'ESO")
                        #Si fa 1r d'ESO
                        if alumne["Curs"] == '1r ESO':
                            #Actualitzar-lo a 2n
                            dbalumnes.update_one(
                                {"Nom":alumne["Nom"]},
                                {"$set": {"Curs": '2n ESO'}}
                            )
                            #Mostrar-ho
                            return rx.toast.success(f"{alumne["Nom"]} de 1r d'ESO passat a 2n d'ESO")
            except Exception as e:
                self.selected_alumne_ids = []
                return rx.toast.error(e)
        else:
            #Si no hi ha cap alumne seleccionat, mostrar-ho
            self.selected_alumne_ids = []
            return rx.toast.error("No hi ha cap alumne seleccionat")
        #Resetejar els aumnes seleccionats al final
        self.selected_alumne_ids = []


#Columnes que es mostren a la taula
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


#Funció front-end principal del modificador d'alumnes
def modificar_alumne() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                #Títol
                rx.heading("Modificar alumnes", color=colors.VERD.value),
                #Input que és un buscador
                rx.input(
                    placeholder="Buscar alumne, curs o correus",
                    on_change=AlumnState.set_search_text,
                    width="99%",
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
                #La taula amb les columnes anteriors
                ag_grid(
                    id="alumnes_grid",
                    column_defs=column_defs,
                    row_data=AlumnState.filtered_alumnes,
                    width="1200px",
                    height="45vh",
                    row_selection="multiple",
                    on_selection_changed=AlumnState.handle_selection_changed,
                ),
                #Input per canviar els correus
                rx.input(
                    placeholder="Posa el nou correu",
                    on_change=AlumnState.set_new_mail,
                    width="99%",
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
                #Botons
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