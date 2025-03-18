### Primer ###
#Fitxer per als alumnes de tercer d'ESO

#importacions
import reflex as rx
from reflex_ag_grid import ag_grid
from bson import ObjectId
from db.db_client import db
from typing import List
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.navbar import navbar
import smtplib
from email.message import EmailMessage
import ssl
import datetime


#Base de dades dels alumnes
dbalumnes = db['alumnes']

# Creo una variable amb tots els alumnes de tercer d'ESO de la base de dades
# Només surten els alumnes que s'han insertat com que fan tercer d'eso
# Tots els altres alumnes no surten
db1 = dbalumnes.find({'Curs': '3r ESO'})


# Creo una classe amb totes les funcions variables... que nescesito per el bak-end.
class AlumneState3r(rx.State):
    # Variables globals de la classe
    alumnes: list[dict] = []
    selected_alumne_ids: List[str] = []
    er_tutor:str = ''
    er_familia:str = ''
    ps = 'contrassenya' 
    e_sender = 'tdrarbat@gmail.com'


    #Funció per trobar el correu del tutor
    def get_tutor_email(self):
        #Si hi ha algun alumne seleccionat:
        if self.selected_alumne_ids and self.alumnes:
            #Variable amb l'alumne seleccionat
            selected_alumne = next(
                (alumno for alumno in self.alumnes if alumno['_id'] in self.selected_alumne_ids), 
                None
            )
            if selected_alumne:
                #Trobar el correu familiar i el del tutor de l'alumne per poder enviar els correus quan hi haigi una falta d'assistencia
                self.er_tutor = selected_alumne.get('Correu del tutor', 'No disponible')
                self.er_familia = selected_alumne.get('Correu familiar', "No disponible")
                #Trornar-los en cas de que la funció fos cridada
                return [self.er_tutor, self.er_familia]
                

    #Load inicial que es crida al add_page()
    def load_alumnes(self):
        #Convertir ObjectId a string per la compatibilitat
        #Només dels alumnes de 3r d'ESO
        raw_alumnes = [
            {**alumne, '_id': str(alumne['_id'])}
            for alumne in dbalumnes.find({'Curs':'3r ESO'})
        ]
        
        #Crear variables de la llista a string i deixar la normal per que sigui compatible
        #Per a la llista on es veuen les hores que s'han posat els retards ha de ser un str si no no és compatible
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


    # Funciò per actualitzar l'_id de cada alumne (a mongodb d'escriu "_id")
    def handle_selection_changed(self, selected_rows: List[dict]):
        # Actualizar els IDs dels alumnes seleccionats
        self.selected_alumne_ids = [str(row['_id']) for row in selected_rows]


    ### INCREMENTAR ###


    # Funciò per incrementar retards dels alumnes seleccionats
    def increment_selected_retards(self):
        try:
            #Si no hi ha cap alumne seleccionat:
            if not self.selected_alumne_ids:
                #Mostrar que no es pot incrementar un retard si no hi ha cap alumne seleccionat
                return rx.toast.error("No hi ha cap alumne seleccionat")
            #Per cada alumne seleccionat (pot ser més de 1)
            for alumne_id in self.selected_alumne_ids:
                #Aconseguir la data actual per guardar el dia i hora en la que s'ha posat el retard
                data_actual = datetime.datetime.now()
                
                #Data formatejada perquè es pugui llegir millor la data
                data_formatejada = {
                    "dia": data_actual.strftime("%d/%m/%Y"),
                    "hora": data_actual.strftime("%H:%M")
                }
                
                # Actualitzar l'alumne a la base de dades
                dbalumnes.update_one(
                    #Trobar l'alumne (buscar per l'_id de l'alumne)
                    {"_id": ObjectId(alumne_id)},
                    {
                        #Incrementar els retards en un
                        "$inc": {"Retards": 1},
                        #Afegir la data a la llista de dies i hores que s'han posat
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
    
    
    # Crear una funcio pera incrementar les faltes justificades
    def increment_selected_faltesj(self):
        try:
            #Si no hi ha cap alumne seleccionat
            if not self.selected_alumne_ids:
                #Mostrar que no es pot sumar una falta justificada si no hi ha cap alumne seleccionat
                return rx.toast.error("No hi ha cap alumne seleccionat")
            #Incrementar faltes justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                #Aconseguir la data actual
                data_actual = datetime.datetime.now()
                
                #Formatejar la data perque sigui més llegible
                data_formatejada = {
                    "dia": data_actual.strftime("%d/%m/%Y"),
                    "hora": data_actual.strftime("%H:%M")
                }
                
                #Actualitzar l'alumne a la base de dades
                dbalumnes.update_one(
                    {"_id": ObjectId(alumne_id)},
                    {
                        #Incrementar les faltes en 1 cada cop
                        "$inc": {"Faltes justificades": 1},
                        #Afegir la data a la llista
                        "$push": {"Llista de faltes justificades": data_formatejada}
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
            #Si no hi ha cap alumne seleccionat
            if not self.selected_alumne_ids:
                #Mostrar que no es pot sumar una falta no justificada
                return rx.toast.error("No hi ha cap alumne seleccionat")
            # Incrementar faltes justificades per als alumnes seleccionats
            for alumne_id in self.selected_alumne_ids:
                #Aconseguir la data actual
                data_actual = datetime.datetime.now()
                
                #Formatejar la data per a una millor lectura
                data_formatejada = {
                    "dia": data_actual.strftime("%d/%m/%Y"),
                    "hora": data_actual.strftime("%H:%M")
                }
                
                #Actualitzar l'alumne
                dbalumnes.update_one(
                    #Trobar l'alumne
                    {"_id": ObjectId(alumne_id)},
                    {
                       #Sumar la falta no justificada i posar la data a la llista 
                        "$inc": {"Faltes no justificades": 1},
                        #Posar la data en la que s'ha posat el retard a la llista
                        "$push": {"Llista de faltes no justificades": data_formatejada}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            self.get_tutor_email()
            
            #enviar el correu
            self.enviar_correu_faltesnj()
            
            # netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            #Retornar que s'ha afegit correctament
            return rx.toast.success("S'ha afegit la falta no justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')
        
        
    ### RESTAR ###
        
        
    # Funcions per restar retards i faltes en cas de que hi haigi un error
    
    #Funció per restar retards
    def restar_selected_retards(self):
        try:
            #Si no hi ha cap alumne seleccionat
            if not self.selected_alumne_ids:
                #Mostrar-ho amb un toast
                return rx.toast.error("No hi ha cap alumne seleccionat")
            #Per cada alumne seleccionat
            for alumne_id in self.selected_alumne_ids:
                #Actualitzar un alumne
                dbalumnes.update_one(
                    #Trobar-lo per l'id
                    {"_id": ObjectId(alumne_id)},
                    {   
                        #Sumar -1 retard
                        #És el mateix que restar-ne un
                        "$inc": {"Retards": -1},
                        #Esborrar l'últim element de la llista de retards
                        "$pop": {"Llista de retards": 1}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            #Aconseguir el correu del tutor
            self.get_tutor_email()
            
            # Enviar correu
            self.enviar_correu_restar_retard()
            
            #Netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            #Retornar que s'ha restat el retard correctament
            return rx.toast.success("S'ha restat el retard correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')
        
        
    # Funcio per restar una falta no justificada a un alumne
    def restar_selected_faltesnj(self):
        try:
            #Si no hi ha cap alumne seleccionat
            if not self.selected_alumne_ids:
                #Mostrar que no hi ha cap alumne seleccionat
                return rx.toast.error("No hi ha cap alumne seleccionat")
            #Per cada alumne seleccionat
            for alumne_id in self.selected_alumne_ids:
                #Actualitzar l'alumne
                dbalumnes.update_one(
                    #Buscar-lo per el seu id
                    {"_id": ObjectId(alumne_id)},
                    {
                        #Restar una falta no justificada
                        "$inc": {"Faltes no justificades": -1},
                        #Treure l'ultim elememt de la llista
                        "$pop": {"Llista de faltes no justificades": 1}
                    }
                )
            
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            #Aconseguir el mail del tutor
            self.get_tutor_email()
            
            #enviar el correu
            self.enviar_correu_restar_faltesnj()
            
            #netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            #Mostrar que tot ha anat correctament
            return rx.toast.success("S'ha afegit la falta no justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')


    # Funcio per restar les faltes justificades
    def restar_selected_faltesj(self):
        try:
            #Si no hi ha cap alumne seleccionat
            if not self.selected_alumne_ids:
                #Mostrar que no hi ha cap alumne seleccionat
                return rx.toast.error("No hi ha cap alumne seleccionat")
            # Incrementar faltes no justificades per als alumnes seleccionats
            #Per cada alumne seleccionat
            for alumne_id in self.selected_alumne_ids:
                #Actualitzar l'alumne
                dbalumnes.update_one(
                    #Buscar-lo per el seu id
                    {"_id": ObjectId(alumne_id)},
                    {
                        #Restar una falta justificada
                        "$inc": {"Faltes justificades": -1},
                        #Treure l'ultim element de la llista
                        "$pop": {"Llista de faltes justificades": 1}
                    }
                )
                
            # Recargar les dades desprès de l'actualitzaciò
            self.load_alumnes()
            
            #Agafar el mail del tutor
            self.get_tutor_email()
            
            # Enviar correu
            self.enviar_correu_restar_faltesj()
            
            # netejar la seccio despres d'incrementar
            self.selected_alumne_ids = []
            
            #Mostrar que tot ha anat correctament
            return rx.toast.success("S'ha restat la falta justificada correctament")
        except Exception as e:
            return rx.window_alert(f'Error: {str(e)}')


    # Que es converteixi de ObjectID a string des del principi
    #Per temes de compatibilitat
    def initial_load(self):
        self.load_alumnes()
        
        
        
    ### CORREUS ###
        
    #Funcions per enviar correus a la familia i al tutor
    
    #Funció pel correu que s'envia quan s'ha posat un retard
    def enviar_correu_retard(self):
        # Verificar si hi ha alumnes seleccionats
        if not self.selected_alumne_ids:
            #Mostrar que no hi ha cap alumne seleccionat
            return rx.toast.success("No hi ha cap alumne seleccionat")

        #El que envia el correu
        e_sender = self.e_sender
        #Contrassenya
        ps = self.ps
        #El que rep el correu
        #En aquest cas el tutor i el familiar
        er = self.er_tutor,self.er_familia

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Retards:\n\n"

        #Per cada alumne seleccionat
        for alumne_id in self.selected_alumne_ids:
            # Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})

            #Si hi ha algún alumne
            if alumne:
                # Afegir linies de text al correu
                #Text amb el nom de l'alummne
                text += f"Avui a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                #Text que informa de que ha arribat tard a classe
                #I el dia i hora en el que s'ha posat
                text += f"Ha arribat tard a classe, el retard s'ha posat a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Retards', 0)} retards.\n\n"

        # Assignar un títol
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
                #Entrar al mail amb la contrassenya i el correu
                smtp.login(e_sender, ps)
                #Enviar correu
                smtp.sendmail(e_sender, er, em.as_string())
                
                #Mostrar que tot ha anat be
            return rx.toast.success("S'ha enviat un correu al tutor correctament")
        # Que fer si hi ha algun error
        except Exception as e:
            #Mostrar l'error
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
    

    #Funció per enviar el correu quan es resta un retard
    def enviar_correu_restar_retard(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            #Mostrar que s'ha de seleccionar algún alumne
            return rx.toast.error("No hi ha cap alumne seleccionat")

        #El que envia el correu
        e_sender = self.e_sender
        #La contrassenya
        ps = self.ps
        #Les persones que reben el correu
        #Que son la familia i tutor de l'alumne
        er = self.er_tutor,self.er_familia

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Retards:\n\n"

        for alumne_id in self.selected_alumne_ids:
            # Buscar l'alumne al la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir textos
                #Text amb el nom
                text += f"S'ha tret un retard a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                #Text amb les dates que s'ha posat
                text += f"Hi ha hagut un error amb el retard posat anteriorment a l'alumne.\n\nEl retard s'ha tret correctement a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Retards', 0)} retards.\n\n"

        # Assignar el títol en una variable
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
                #Entrar amb la contrassenya
                smtp.login(e_sender, ps)
                #Enviar els correus amb els parametres anteriors
                smtp.sendmail(e_sender, er, em.as_string())

            #Retornar que tot ha sortit correctament
            return rx.toast.success("Correu enviat correctament")
        # Que fer si falla
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
    
    #Enviar el correu per a les faltes no justificades
    def enviar_correu_faltesnj(self):
        # Verificar si hi ha algun alumne seleccionat
        if not self.selected_alumne_ids:
            #Retornar que no hi ha cap alumne seleccionat
            return rx.toast.error("No hi ha cap alumne seleccionat")

        #Variable per saber qui envia el correu
        e_sender = self.e_sender
        #La contrassenya
        ps = self.ps
        #Els que reben el correu
        #Tutor i familia de l'alumne
        er = self.er_tutor,self.er_familia

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes no justificades:\n\n"

        #Per cada alumne seleccionat
        for alumne_id in self.selected_alumne_ids:
            #Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                #Informació sobre l'alumne
                text += f"Avui a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                #Informació sobre el moment de posar el retard
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
                #Entrar al mail
                smtp.login(e_sender, ps)
                #Enviar-ho
                smtp.sendmail(e_sender, er, em.as_string())
            
            #Retornar que ha funcionat
            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            #Mostrar l'error
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
    #Enviar el correu per restar la falta no justificada
    def enviar_correu_restar_faltesnj(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            #Mostrar que no hi ha cap alumne
            return rx.toast.error("No hi ha cap alumne seleccionat")

        #El que envia el correu
        e_sender = self.e_sender
        #La contrassenya
        ps = self.ps
        #Els que reben el correu
        #Familia i tutor
        er = self.er_tutor,self.er_familia

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes no justificades:\n\n"

        #Per cada alumne seleccionat
        for alumne_id in self.selected_alumne_ids:
            # Buscar l'alumne a la base dedades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                #Text sobre l'alumne
                text += f"S'ha tret una falta no justificada a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                #Informació sobre la falta
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
                #Entrar al correu
                smtp.login(e_sender, ps)
                #Enviar el correu
                smtp.sendmail(e_sender, er, em.as_string())

            #Mostrar que tot ha funcionat 
            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            #Mostrar l'error
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
    
    
    #Enviar un correu per a les faltes justificades
    def enviar_correu_faltesj(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            #Mostrar que no hi ha cap alumne seleccionat
            return rx.toast.error("No hi ha cap alumne seleccionat")

        #El que envia el correu
        e_sender = self.e_sender
        #La contrassenya
        ps = self.ps
        #El que rep el correu
        #En aquest cas la familia i el tutor
        er = self.er_tutor,self.er_familia

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes justificades:\n\n"

        #Per cada alumne seleccionat
        for alumne_id in self.selected_alumne_ids:
            # Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                
                #text sobre l'alumne
                text += f"Avui a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                #Text sobre la falta
                text += f"Li han posat una falta justificada, la falta justificada s'ha posat a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment en té: {alumne.get('Faltes justificades', 0)} faltes justificades. \n\n"

        #Assignar un títol
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
                #Entrar al correu
                smtp.login(e_sender, ps)
                #Enviar-lo
                smtp.sendmail(e_sender, er, em.as_string())

            #Mostrar que s'ha enviat
            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            #Mostrar l'error
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
        
    #Enviar el correu per restar les faltes justificades
    def enviar_correu_restar_faltesj(self):  
        # Verificar si hi han alumnes seleccionats
        if not self.selected_alumne_ids:
            #Si no hi han alumnes seleccionats
            #Mostrar que no n'hi ha
            return rx.toast.error("No hi ha cap alumne seleccionat")

        #El que envia el correu
        e_sender = self.e_sender
        #La contrassenya
        ps = self.ps
        #El que rep el correu
        #Familia i tutor
        er = self.er_tutor,self.er_familia

        # Preparar el text del correu amb l'informacio dels retards
        text = "Informe de Faltes justificades:\n\n"

        #Per cada alumne seleccionat
        for alumne_id in self.selected_alumne_ids:
            # Buscar l'alumne a la base de dades
            alumne = dbalumnes.find_one({"_id": ObjectId(alumne_id)})
        
            if alumne:
                # Afegir text
                
                #Text sobre l'alumne
                text += f"S'ha tret una falta justificada a l'alumne/a: {alumne.get('Nom', 'Sense nom')}\n"
                #Text sobre la falta
                text += f"Hi ha hagut un error amb la falta justificada posada anteriorment a l'alumne.\n\nLa falta justificada s'ha tret correctement a les {datetime.datetime.now().strftime('%H:%M')} del dia {datetime.datetime.now().day}/{datetime.datetime.now().month}/{datetime.datetime.now().year} i actualment té: {alumne.get('Faltes justificades', 0)} faltes justificades.\n\n"

        #Variable amb el títol
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
                #Entrar al correu
                smtp.login(e_sender, ps)
                #Enviar-lo
                smtp.sendmail(e_sender, er, em.as_string())

            return rx.toast.success("Correu enviat correctament")
        # Que fer si hi ha un error
        except Exception as e:
            return rx.window_alert(f'Error en enviar el correu: {str(e)}')
        
    
    
    
        
#Funció fora de la calasse per fomatejar les dates
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
#Taula amb tots els alumnes 
column_defs = [
    # Columne per seleccionar al alumne
    #Check box
    ag_grid.column_def(
        align = 'center',
        field="selected", 
        header_name="", 
        checkboxSelection=True,
        headerCheckboxSelection=True,
        width='50%'
    ),
    # Columna per el nom
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


#Una variable amb les columnes que hi ha a la taula quan es canvii per el botó
#Taula per veure els horaris que s'han posat els retards
all_columns = [
    #Columna pel nom del alumne
    ag_grid.column_def(
        field="Nom",
        header_name="Nom",
        width='250%'
    ),
    #Columne per la llista de retards
    ag_grid.column_def(
        field='retards_list',
        header_name="Lista de retards",
        width='315%',
        autoHeight=True,
        wrapText=True
    ),
    #Columna per la llista de faltes no justificades
    ag_grid.column_def(
        field='faltesnj_list',
        header_name="Lista de faltes no justificades",
        width='315%',
        autoHeight=True,
        wrapText=True
    ),
    #Columna per les faltes justificades
    ag_grid.column_def(
        field='faltesj_list',
        header_name='Llista de faltes justificades',
        width='315%',
        autoHeight=True,
        wrapText=True
    )
]


#Classe amb totes les variables i funcions nescessaries per canviar les taules
class Show_Column(rx.State):
    #Variable que conta el nombre de clicks que es dona a un botó
    #Després es podrá veure que si el nombre de clicks és parell o inparell es mostra una cosa o una altre
    #Inicialment té un valor de 0
    n_clicks:int = 0
    
    
    #Funció en la que se suma un click més a la variable anterior
    #Cada cop que s'apreta el botó se suma un click
    def more_clicks(self):
        #Ordre que es dona per sumar clicks
        self.n_clicks += 1


# Funciò front-end per als alumnes de tercer d'ESO
def front_tercer():
    return rx.box(
        #Cridar la navbar
        navbar(),
        rx.center(
            rx.vstack(
                # Titol
                rx.heading(
                    #Text
                    "Gestió d'estudiants de 3r d'ESO",
                    #Mida
                    size="7",
                    #Aliniar títol
                    align='center',
                    #Color del text
                    color=colors.VERD.value
                ),
                rx.hstack(
                    # Botons de la part superior
                    # Boto d'afegrir retards
                    rx.button(
                        #Text del botó
                        "Sumar Retards", 
                        #que fer quan s'apreta
                        #Crida la funció que incrementa retards
                        on_click=AlumneState3r.increment_selected_retards,
                        #Color de fons
                        background_color=colors.PRIMARY.value,
                        #Amplada
                        width = '240px'
                    ),
                    
                    # Boto d'afegir faltes no justificades
                    rx.button(
                        #Text del boto
                        "Sumar faltes no justificades",
                        #Quan es clica incrementa les faltes no justificades
                        on_click=AlumneState3r.increment_selected_faltesnj,
                        #Color de fons
                        background_color = colors.PRIMARY.value,
                        #Amplada
                        width = '243px'
                    ),
                    
                    # Boto d'afegir faltes justificades
                    rx.button(
                        #Text del botó
                        "Sumar faltes justificades",
                        #Quan es clica crida la funció  de sumar una falta justificada
                        on_click=AlumneState3r.increment_selected_faltesj,
                        #Color de fons
                        background_color = colors.PRIMARY.value,
                        #Amplada
                        width = '243px'
                    ),
                    # Parametres per fer-ho mes bonic
                    #Espai entre elements
                    spacing="3",
                    #Centrar-ho al mig
                    align='start'
                ),
                #Botó per canviar la info que es veu
                rx.button(
                    #text del botó
                    'Veure informació',
                    #Quan es clica crida la funció
                    #Suma un punt per cada click
                    on_click=Show_Column.more_clicks(),
                    #Color de fons
                    background_color=colors.VERD.value,
                ),

                # Posar la variable de la taula d'alumnes que he fet anteriorment
                # Afegir molts parametres estetics
                ag_grid(
                    #ID
                    id="student_grid",
                    #Les columnes anteriors
                    column_defs=rx.cond(
                            #Si el nº de clicks es parell
                            Show_Column.n_clicks % 2 == 0,
                            #Mostrar una columna
                            column_defs,
                            #Les altres columnes
                            all_columns
                        ),
                    #Agafar els alumnes de tercer d'eso com a dades
                    row_data=AlumneState3r.alumnes,
                    #Amplada de la taula
                    width="1200px",
                    #Altura de la taula
                    height="45vh",
                    #Es pot seleccionar més d'un alumne
                    row_selection="multiple",
                    #Funció per quan es canvi l'alumne seleccionat3
                    on_selection_changed=AlumneState3r.handle_selection_changed,
                    z_index = '0%'
                ),
                # Botons de la part inferior
                #Stack horitzontal on es guarden els botons
                rx.hstack(
                    # Boto per restar retards
                    rx.button(
                        #Text del botó
                        "Restar Retards", 
                        #Qan s'apreta es crida la funció de restar retards
                        on_click=AlumneState3r.restar_selected_retards,
                        #Color de fons
                        background_color=colors.PRIMARY.value,
                        #Amplada
                        width = '240px'
                    ),
                    
                    # Boto per restar fales no justificades
                    rx.button(
                        #Text del botó
                        "Restar faltes no justificades",
                        #Que al ser apretat cridi la funció de restar la falta no justificada
                        on_click=AlumneState3r.restar_selected_faltesnj,
                        #Color de fons
                        background_color = colors.PRIMARY.value,
                        #Amplada
                        width = '243px'
                    ),
                    
                    # Boto per restar faltes justificades
                    rx.button(
                        #Text del botó
                        "Restar faltes justificades",
                        #Que quan s'apreti es cridi a la funció de restar faltes justificades
                        on_click=AlumneState3r.restar_selected_faltesj,
                        #Color de fons
                        background_color = colors.PRIMARY.value,
                        #Amplada a 243px
                        width = '243px'
                    ),
                    # Parametres estetics per els botons
                    #Spacing de 3 
                    #Perquè hi haigi bastant espai entre elements
                    spacing="3",
                    #Aliniar elements al centre
                    align='center'
                ),
                #Aliniar el contingut al centre
                align = 'center'
            ),
            # Parametres estetics globals
            #Amplada que ocupi el 100%
            width="100%",
            #Marge exterior de 8em
            padding="8em",
            #Aliniar tots els altres al centre
            align = 'center'
        ),
        #Amplada global a l00%
        #Altura global al 100%
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
    