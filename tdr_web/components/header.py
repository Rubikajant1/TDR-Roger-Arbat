### Header ###
#Cos de la pàgina principal

#Importacions
import reflex as rx
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.link_button import link_button
from tdr_web.components.link_title import title
from db.db_client import db


# Base de dades per als alumnes
dbalumnes = db['alumnes']

#Classe per al back-end (Passar de curs i de trimestre)
class Estat(rx.State):
    confirmar_curs:bool = False
    confirmar_trimestre:bool = False
    pts_curs:int = 1
    pts_trimestre:int = 1
    contrassenya_curs:str
    contrassenya_trimestre:str
    
    
    @rx.event
    def send_contrassenya_trimestre(self,new_password):
        self.contrassenya_trimestre = new_password
    
    @rx.event
    def send_contrassenya_curs(self,new_password):
        self.contrassenya_curs = new_password
    
    def canviar_pts_curs(self):
        self.pts_curs+=1
        self.pts_trimestre+=1
        if self.pts_curs%2==0:
            self.confirmar_trimestre=False
            self.confirmar_curs=True
        else:
            self.confirmar_curs=False
            self.confirmar_trimestre=False
            
    def canviar_pts_trimestre(self):
        self.pts_trimestre+=1
        self.pts_curs+=1
        if self.pts_trimestre%2==0:
            self.confirmar_trimestre=True
            self.confirmar_curs=False
        else:
            self.confirmar_trimestre=False
            self.confirmar_curs=False
    
    def passar_curs(self):
        try:
            quart = list(dbalumnes.find({'Curs':'4t ESO'}))
            if quart:
                resultats_eliminacio=dbalumnes.delete_many({'Curs':'4t ESO'})
                rx.toast.success(f"Alumnes de 4t d'ESO eliminats: {resultats_eliminacio.deleted_count}")
                
            for curs_actual, nou_curs in [('3r ESO','4t ESO'),('2n ESO','3r ESO'),('1r ESO','2n ESO')]: # En ordre al reves perque si no es posa a 4t d'eso perque de primer pasa a segon de segon a tercer i després a quart
                resultat = dbalumnes.update_many(
                    {'Curs': curs_actual}, 
                    {'$set': {
                        'Curs': nou_curs,
                        'Retards':0,
                        'Faltes justificades':0,
                        'Faltes no justificades':0,
                        "Llista de retards":[],
                        "Llista de faltes justificades":[],
                        "Llista de faltes no justificades":[]
                    }}                    
                        
                )
            return rx.toast.success(f"Alumnes canviats de curs correctament {resultat.modified_count}")
        except Exception as e:
            print(e)
            return rx.toast.error(f'Error al actualitzar els alumnes: {e}')
        
        
    def passar_trimestre(self):
        try:
            for curs_actual in ["4t ESO","3r ESO","2n ESO","1r ESO"]: # En ordre al reves perque si no es posa a 4t d'eso perque de primer pasa a segon de segon a tercer i després a quart
                resultat = dbalumnes.update_many(
                    {'Curs': curs_actual}, 
                    {'$set': {
                        'Retards':0,
                        'Faltes justificades':0,
                        'Faltes no justificades':0,
                        "Llista de retards":[],
                        "Llista de faltes justificades":[],
                        "Llista de faltes no justificades":[]
                    }}                    
                        
                )
            return rx.toast.success(f"Trimestre reiniciat correctament")
        except Exception as e:
            print(e)
            return rx.toast.error(f'Error al actualitzar els alumnes: {e}')


#Funció front-end 
def header() -> rx.Component:
    from tdr_web.tdr_web import Verify
    is_autenticated = Verify.user["Autoritzat"]
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.image(
                    src="/logoxandri.jpg",
                    width="8em",
                    height="8em",
                    border_radius="md",
                    object_fit="cover",
                    alt="Logo IE Josep maria xandri"
                ),
                #Titol i text de presentació
                rx.vstack(
                    title(
                        "IE Josep Maria Xandri",
                    ),
                    rx.text(
                        "Registre d'alumnes de secundària",
                        margin_top="0px !important"
                    ),
                    align_items="flex_start"
                ),
                margin_top="2.5em",
                spacing="4",
                align='center'
            ),
            #Text introductiu
            rx.text(
                f"""Aquesta pàgina web serveix per millorar la forma que es posen els retards,
                faltes justificades i no justificades als alumnes de secundària de l'IE Josep Maria Xandri.
                """,
                padding = '2em'
            ),
            #Botons que accedeixen al curs corresponent
            link_button("Alumnes de 1r d'ESO",'Comunitat de joves','/primer',False),
            link_button("Alumnes de 2n d'ESO",'Comunitat de joves','/segon', False),
            link_button("Alumnes de 3r d'ESO",'Comunitat de joves','/tercer', False),
            link_button("Alumnes de 4t d'ESO",'Comunitat de joves','/quart', False),
            #Amb el cond es posa com a parametre de que si esta autenticat
            #Si ho està es mostra tot el que hi haigi a dintre
            #Si no no es mostra ni s'interactua amb els botons
            rx.cond(    
                is_autenticated,
                rx.box(rx.button(
                        rx.hstack(
                            rx.icon(
                                tag='arrow-big-right',
                                color='white'
                            ),
                            rx.vstack(
                                rx.text("Passar de trimestre", color='white', size='4'),
                                rx.text("Resetejar els retards, faltes justificades i no justificades de tots els alumnes", color='white')
                            ),               
                            width='580px',
                            margin='1em',
                            color='white',
                        ),
                        size='2',
                        radius='medium',
                        background_color='#2e8b57',
                        on_click=Estat.canviar_pts_trimestre()
                    ),
                    #Textos on s'alarma del que passarà
                    rx.cond(
                        Estat.confirmar_trimestre,
                        rx.text("Estàs segur que vols passar de trimestre?", margin="0.3em"),
                    ),
                    rx.cond(
                        Estat.confirmar_trimestre,
                        rx.text("Tots els retards, faltes justificades i no justifades seran resetejades")
                    ),
                    #Botó per confirmar que es vol passar de trimestre
                    rx.cond(
                        Estat.confirmar_trimestre,
                        rx.button(
                            'Confirmar',
                            background_color=colors.VERD.value,
                            width='100%',
                            on_click=Estat.passar_trimestre(),
                            margin_bottom='4em',
                            margin = "0.3em"
                        )
                    )
                )
            ),
            rx.cond(
                is_autenticated,
                rx.box(
                    #Botó principal per passar de curs
                    rx.button(
                        rx.hstack(
                            rx.icon(
                                tag='arrow-big-right',
                                color='white'
                            ),
                            rx.vstack(
                                rx.text("Passar de curs", color='white', size='4'),
                                rx.text("Passar a tots els alumnes de curs", color='white')
                            ),               
                            width='580px',
                            margin='1em',
                            color='white',
                        ),
                        size='2',
                        radius='medium',
                        background_color='#2e8b57',
                        on_click=Estat.canviar_pts_curs()
                    ),
                    #Un cop apretat el botó surten dos textos especificant el que pot passar
                    rx.cond(
                        Estat.confirmar_curs,
                        rx.text("Estàs segur que vols passar a tots els alumnes de curs?")
                    ),
                    rx.cond(
                        Estat.confirmar_curs,
                        rx.text("Tots els alumnes de 4t d'ESO seran eliminats")
                    ),
                    # Si s'ha apretat el primer botó surt aquest per confirmar que no está fet per error
                    rx.cond(
                        Estat.confirmar_curs,
                        rx.button(
                            'Confirmar',
                            background_color=colors.VERD.value,
                            width='100%',
                            on_click=Estat.passar_curs(),
                            margin_bottom='4em'
                        )
                    ),
                )
            ),
            #Botó (tant per els usuaris com per els administradors) que està fora del cond(d'aquesta manera tothom hi pot accedir)
            rx.button(
               "Tancar sessió",
                on_click=Verify.logout,
                color_scheme="red",
                width='100%',
                height="30px",
                margin_top="20px"
            ),
            margin = '1em'
        )
    )
    