### tercer.py ###

#importacions
import reflex as rx
from reflex_ag_grid import ag_grid
from bson import ObjectId
from db.db_client import db_client
from typing import List
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.navbar import navbar
import smtplib
from email.message import EmailMessage
import ssl
import datetime


# Creo una variable amb totse els alumnes de tercer d'ESO de la base de dades
# Només surten els alumnes que s'han insertat com que fan tercer d'eso
# Tots els altres alumnes no surten

db = db_client['alumnes']

# Obtener la colección (importante!)
dbalumnes = db['alumnes']  # o el nombre de tu colección

# Ahora sí podemos usar find()
db1 = dbalumnes.find({'Curs': '3r ESO'})

# Creo una classe amb totes les funcions variables... que nescesito per el bakend.

class AlumneState3r(rx.State):
    # Variables globals de la classe
    alumnes: list[dict] = []
    selected_alumne_ids: List[str] = []
    er:str
    ps = 'twvf hlgm psfq swdk' 
    e_sender = 'tdrarbat@gmail.com'

    def get_tutor_email(self):
        # Metode per trobar el correu del tutor individual de l'alumne
        if self.selected_alumne_ids and self.alumnes:
            selected_alumno = next(
                (alumno for alumno in self.alumnes if alumno['_id'] in self.selected_alumne_ids), 
                None
            )
            if selected_alumno:
                self.er = selected_alumno.get('Correu del tutor', 'No disponible')
                return self.er
                
        print('Cap alumne seleccionat')
        

    def load_alumnes(self):
    # Convertir ObjectId a string per la compatibilitat
        raw_alumnes = [
            {**alumne, '_id': str(alumne['_id'])}
            for alumne in dbalumnes.find({'Curs':'3r ESO'})
        ]
        
        # Crear variables de la llista a string i deixar la normal per que sigui compatible
        self.alumnes = [
            {
                **alumno,
                "retards_list": str(alumno.get('Llista de retards', [])),
                "Llista de retards": alumno.get('Llista de retards', []),
                "faltesnj_list": str(alumno.get('Llista de faltes no justificades', [])),
                "Llista de faltes no justificades": alumno.get('Llista de faltes no justificades', []),
                "faltesj_list": str(alumno.get('Llista de faltes justificades', [])),
                "Llista de faltes justificades": alumno.get('Llista de faltes justificades', []), 
            }
            # Cicle for per a cada alumne de la variable row alumnes creada anteriorment
            for alumno in raw_alumnes
        ]


    # Funciò per actualitzar els id de cada alumne
    def handle_selection_changed(self, selected_rows: List[dict]):
        # Actualizar els IDs dels alumnes seleccionats
        self.selected_alumne_ids = [str(row['_id']) for row in selected_rows]


    ### INCREMENTAR ###


    # Funciò per incrementar retards
    def increment_selected_retards(self):
        try:
            if not self.selected_alumne_ids:
                return rx.window_alert("No hi ha cap alumne seleccionat")
            # Incrementar faltes justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                data_actual = datetime.datetime.now()
                
                data_formatejada = {
                    "dia": data_actual.strftime("%d/%m/%Y"),
                    "hora": data_actual.strftime("%H:%M")
                }
                
                # Actualitzar l'alumne a la base de dades
                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                    "$inc": {"Retards": 1},
                    "$push": {"Llista de retards": data_formatejada}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            # Cridar la funcio d'enviar el correu al tutor perque estigui informat del retard
            self.get_tutor_email()
            
            # Enviar correu
            self.enviar_correu_retard()
            
            # Netejar la seccio despres d'incrementar
            # Per si es canvia d'alumne
            self.selected_alumne_ids = []
            
            #Retornar un toast dient que ha funcionat
            return rx.toast.success("S'ha afegit el retard")
        except Exception as e:
            # Retornar un window alert per si no ha funcionat
            return rx.window_alert(f'Error: {str(e)}')
    
    
    # Crear una funcio per les faltes justificades
    def increment_selected_faltesj(self):
        try:
            if not self.selected_alumne_ids:
                return rx.window_alert("No hi ha cap alumne seleccionat")
            # Incrementar faltes justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                data_actual = datetime.datetime.now()
                
                fecha_formateada = {
                    "dia": data_actual.strftime("%d/%m/%Y"),
                    "hora": data_actual.strftime("%H:%M")
                }
                
                # Actualitzar l'alumne a la base de dades
                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                    "$inc": {"Faltes justificades": 1},
                    "$push": {"Llista de faltes justificades": fecha_formateada}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            self.get_tutor_email()
            
            # Enviar correu
            self.enviar_correu_faltesj()
            
            # Netejar la seccio despres d'incrementar
            # Per si es canvia d'alumne
            self.selected_alumne_ids = []
            
            return rx.toast.success("S'ha afegit la falta justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')
        
        
    #Funcio per incrementar les falates no justificades
    def increment_selected_faltesnj(self):
        try:
            if not self.selected_alumne_ids:
                return rx.window_alert("No hi ha cap alumne seleccionat")
            # Incrementar faltes justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                data_actual = datetime.datetime.now()
                
                fecha_formateada = {
                    "dia": data_actual.strftime("%d/%m/%Y"),
                    "hora": data_actual.strftime("%H:%M")
                }

                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                    "$inc": {"Faltes no justificades": 1},
                    "$push": {"Llista de faltes no justificades": fecha_formateada}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            self.get_tutor_email()
            
            #enviar el correu
            self.enviar_correu_faltesnj()
            
            # netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            return rx.toast.success("S'ha afegit la falta no justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')
        
        
        ### RESTAR ###
        
        
    # Funcio per restar un retard a l'alumne seleccionat
    def restar_selected_retards(self):
        try:
            if not self.selected_alumne_ids:
                return rx.window_alert("No hi ha cap alumne seleccionat")
            # restar retards per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                        "$inc": {"Retards": -1},
                        "$pop": {"Llista de retards": 1}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            self.get_tutor_email()
            
            # Enviar correu
            self.enviar_correu_restar_retard()
            
            # netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            return rx.toast.success("S'ha restat el retard correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')
        
        
    # Funcio per restar una falta no justificada a un alumne
    def restar_selected_faltesnj(self):
        try:
            if not self.selected_alumne_ids:
                return rx.window_alert("No hi ha cap alumne seleccionat")
            # Incrementar faltes no justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                        "$inc": {"Faltes no justificades": -1},
                        "$pop": {"Llista de faltes no justificades": 1}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            self.get_tutor_email()
            
            #enviar el correu
            self.enviar_correu_restar_faltesnj()
            
            # netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            return rx.toast.success("S'ha afegit la falta no justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')


    # Funcio per restar les faltes justificades
    def restar_selected_faltesj(self):
        try:
            if not self.selected_alumne_ids:
                return rx.window_alert("No hi ha cap alumne seleccionat")
            # Incrementar faltes no justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                        "$inc": {"Faltes justificades": -1},
                        "$pop": {"Llista de faltes justificades": 1}
                    }
                )
                
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            self.get_tutor_email()
            
            # Enviar correu
            self.enviar_correu_restar_faltesj()
            
            # netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            return rx.toast.success("S'ha restat la falta justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')


    # Que es converteixi de ObjectID a string des del principi
    def initial_load(self):
        self.load_alumnes()
        
    ### CORREUS ###
        
        
    def enviar_correu_retard(self):
        # Verificar si hi ha alumnes seleccionats
        if not self.selected_alumne_ids:
            return rx.window_alert("No hi ha cap alumne seleccionat")

        e_sender = self.e_sender
        ps = self.ps
        er = self.er

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Retards:\n\n"

        for alumne_id in self.selected_alumne_ids:
                # Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir linies de text al correu
                text += f"Avui a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                text += f"Ha arribat tard a classe, el retard s'ha posat a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Retards', 0)} retards.\n\n"

        # Assignar un titol
        titol = 'Informe de Retards'

        # Indicar com s'ha d'enviar
        em = EmailMessage()
        em['from'] = e_sender
        em['to'] = er
        em['subject'] = titol
        em.set_content(text)

        context = ssl.create_default_context()

        try:
            # Enviar el correu
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(e_sender, ps)
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("S'ha enviat un correu al tutor correctament")
        # Que fer si hi ha algun error
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
    
    
      
    def enviar_correu_restar_retard(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            return rx.window_alert("No hi ha cap alumne seleccionat")

        e_sender = self.e_sender
        ps = self.ps
        er = self.er

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Retards:\n\n"

        for alumne_id in self.selected_alumne_ids:
                # Buscar l'alumne al la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                text += f"S'ha tret un retard a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                text += f"Hi ha hagut un error amb el retard posat anteriorment a l'alumne.\n\nEl retard s'ha tret correctement a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Retards', 0)} retards.\n\n"

        # Assignar el titol en una variable
        titol = 'Informe de Retards'
        
        # Especificar com s'ha d'enviar el correu
        em = EmailMessage()
        em['from'] = e_sender
        em['to'] = er
        em['subject'] = titol
        em.set_content(text)

        context = ssl.create_default_context()

        try:
            # Enviar correu
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(e_sender, ps)
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("Correu enviat correctament")
        # Que fer si falla
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
        
    def enviar_correu_faltesnj(self):
        # Verificar si hi ha algun alumne seleccionat
        if not self.selected_alumne_ids:
            return rx.window_alert("No hi ha cap alumne seleccionat")

        e_sender = self.e_sender
        ps = self.ps
        er = self.er

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes no justificades:\n\n"

        for alumne_id in self.selected_alumne_ids:
                # Buscar el alumno en la base de datos
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                text += f"Avui a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                text += f"Li han posat una falta no justificada, la falta no justificada s'ha posat a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment en té: {alumne.get('Faltes no justificades', 0)} faltes no justificades. \n\n"

        # Assignar una variable al titol
        titol = 'Informe de faltes no justificades'

        # Especificar com s'ha d'enviar
        em = EmailMessage()
        em['from'] = e_sender
        em['to'] = er
        em['subject'] = titol
        em.set_content(text)

        context = ssl.create_default_context()

        try:
            # Enviar correu
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(e_sender, ps)
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
    
    def enviar_correu_restar_faltesnj(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            return rx.window_alert("No hi ha cap alumne seleccionat")

        e_sender = self.e_sender
        ps = self.ps
        er = self.er

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes no justificades:\n\n"

        for alumne_id in self.selected_alumne_ids:
                # Buscar l'alumne a la base dedades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                text += f"S'ha tret una falta no justificada a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                text += f"Hi ha hagut un error amb la falta no justificada posada anteriorment a l'alumne.\n\nLa falta no justificada s'ha tret correctement a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Faltes no justificades', 0)} faltes no justificades.\n\n"

        # Assignar una variable de titol
        titol = 'Informe de faltes no justificades'

        #Especificar com s'ha d'enviar el correu
        em = EmailMessage()
        em['from'] = e_sender
        em['to'] = er
        em['subject'] = titol
        em.set_content(text)

        context = ssl.create_default_context()

        try:
            # Enviar el correu
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(e_sender, ps)
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
    
    
    def enviar_correu_faltesj(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            return rx.window_alert("No hi ha cap alumne seleccionat")

        e_sender = self.e_sender
        ps = self.ps
        er = self.er

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes justificades:\n\n"

        for alumne_id in self.selected_alumne_ids:
                # Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                text += f"Avui a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                text += f"Li han posat una falta justificada, la falta justificada s'ha posat a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment en té: {alumne.get('Faltes justificades', 0)} faltes justificades. \n\n"

        titol = 'Informe de faltes justificades'

        # Especificar com s'ha d'enviar el correu
        em = EmailMessage()
        em['from'] = e_sender
        em['to'] = er
        em['subject'] = titol
        em.set_content(text)

        context = ssl.create_default_context()

        try:
            # Enviar el correu
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(e_sender, ps)
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
        
    def enviar_correu_restar_faltesj(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            return rx.window_alert("No hi ha cap alumne seleccionat")

        e_sender = self.e_sender
        ps = self.ps
        er = self.er

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes justificades:\n\n"

        for alumne_id in self.selected_alumne_ids:
                # Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                text += f"S'ha tret una falta justificada a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                text += f"Hi ha hagut un error amb la falta justificada posada anteriorment a l'alumne.\n\nLa falta justificada s'ha tret correctement a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Faltes justificades', 0)} faltes justificades.\n\n"

        titol = 'Informe de Faltes justificades'

        # Especificar com s'ha d'enviar el correu
        em = EmailMessage()
        em['from'] = e_sender
        em['to'] = er
        em['subject'] = titol
        em.set_content(text)

        context = ssl.create_default_context()

        try:
            # Enviar correu
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(e_sender, ps)
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
    
    
    
        

def format_date_list(date_list):
    if not date_list:
        return ""
    
    formatted_dates = []
    for entry in date_list:
        if isinstance(entry, dict):
            date = entry.get('dia', '')
            time = entry.get('hora', '')
            formatted_dates.append(f"{date} {time}")
    
    return "\n".join(formatted_dates)



# Variable amb totes les columnes de la taula
column_defs = [
    # Columne per seleccionar al alumne
    ag_grid.column_def(
        align = 'center',
        field="selected", 
        header_name="", 
        checkboxSelection=True,
        headerCheckboxSelection=True,
        width='50%'
    ),
    # Columne per el nom
    ag_grid.column_def(
        field="Nom",
        header_name="Nom",
        width='400%'
    ),
    # Columne pels retards
    ag_grid.column_def(
        field="Retards", 
        header_name="Retards",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width = '249%'
    ),
    # Columne per les faltes no justificades
    ag_grid.column_def(
        field="Faltes no justificades", 
        header_name="Faltes no justificades",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width='249%',
    ),
    # Columne per les faltes justificades
    ag_grid.column_def(
        field="Faltes justificades", 
        header_name="Faltes justificades",
        cellRenderer="agAnimateShowChangedCellRenderer",
        width = '249%',
        text_align = 'center'
    )
]

all_columns = [
    ag_grid.column_def(
        field="Nom",
        header_name="Nom",
        width='250%'
    ),
    ag_grid.column_def(
        field='retards_list',
        header_name="Lista de retards",
        width='315%',
        autoHeight=True,
        wrapText=True
    ),
    ag_grid.column_def(
        field='faltesnj_list',
        header_name="Lista de faltes no justificades",
        width='315%',
        autoHeight=True,
        wrapText=True
    ),
    ag_grid.column_def(
        field='faltesj_list',
        header_name='Llista de faltes justificades',
        width='315%',
        autoHeight=True,
        wrapText=True
    )
]


all_columns = [
    ag_grid.column_def(
        field="Nom",
        header_name="Nom",
        width='400%',
    ),
    ag_grid.column_def(
        field='retards_list',
        header_name="Lista de retards",
        width='250%',
        autoHeight=True,
        wrapText=True
    ),
    ag_grid.column_def(
        field='faltesnj_list',
        header_name="Lista de faltes no justificades",
        width='250%',
        autoHeight=True,
        wrapText=True
    ),
    ag_grid.column_def(
        field='faltesj_list',
        header_name='Llista de faltes justificades',
        width='250%',
        autoHeight=True,
        wrapText=True
    )
]

class Show_Column(rx.State):
    n_clicks:int = 0
    
    def more_clicks(self):
        self.n_clicks += 1


# Funciò frontendo
def front_tercer():
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                # Titol
                rx.heading("Gestió d'estudiants de 3r d'ESO", size="7",align='center',color=colors.VERD.value),
                rx.hstack(
                    # Botons de la part superior
                    # Boto d'afegrir retards
                    rx.button(
                        "Sumar Retards", 
                        on_click=AlumneState3r.increment_selected_retards,
                        background_color=colors.PRIMARY.value,
                        width = '240px'
                    ),
                    # Boto d'afegir faltes no justificades
                    rx.button(
                        "Sumar faltes no justificades",
                        on_click=AlumneState3r.increment_selected_faltesnj,
                        background_color = colors.PRIMARY.value,
                        width = '243px'
                    ),
                    # Boto d'afegir faltes justificades
                    rx.button(
                        "Sumar faltes justificades",
                        on_click=AlumneState3r.increment_selected_faltesj,
                        background_color = colors.PRIMARY.value,
                        width = '243px'
                    ),
                    # Parametres per fer-ho mes maco
                    spacing="3",
                    align='start'
                ),
                rx.button('Veure les hores', on_click=Show_Column.more_clicks(), background_color=colors.VERD.value,),

                # Posar la variable de la taula d'alumnes que he fet anteriorment
                # Afegir molts parametres estetics
                ag_grid(
                    id="student_grid",
                    column_defs=rx.cond(
                            Show_Column.n_clicks % 2 == 0,
                            column_defs,
                            all_columns
                        ),
                    row_data=AlumneState3r.alumnes,
                    width="1200px",
                    height="45vh",
                    row_selection="multiple",
                    on_selection_changed=AlumneState3r.handle_selection_changed,
                    z_index = '0%'
                ),
                # Botons de la part inferior
                rx.hstack(
                    # Boto per restar retards
                    rx.button(
                        "Restar Retards", 
                        on_click=AlumneState3r.restar_selected_retards,
                        background_color=colors.PRIMARY.value,
                        width = '240px'
                    ),
                    # Boto per restar fales no justificades
                    rx.button(
                        "Restar faltes no justificades",
                        on_click=AlumneState3r.restar_selected_faltesnj,
                        background_color = colors.PRIMARY.value,
                        width = '243px'
                    ),
                    # Boto per restar faltes justificades
                    rx.button(
                        "Restar faltes justificades",
                        on_click=AlumneState3r.restar_selected_faltesj,
                        background_color = colors.PRIMARY.value,
                        width = '243px'
                    ),
                    # Parametres estetics per els botons
                    spacing="3",
                    align='center'
                ),
                align = 'center'
            ),
            # Parametres estetics globals
            width="100%",
            padding="8em",
            align = 'center'
        ),
        width="100%",
        height="100%",
    )

    
def tercer() -> rx.Component:
    from tdr_web.tdr_web import Verify, login_page
    return rx.cond(
        Verify.is_authenticated,
        front_tercer(),
        login_page()
    )