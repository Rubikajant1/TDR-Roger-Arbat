### Link button ###
#Fitxer amb una funció que crea un botó amb uns estils generals els quals seràn fets servir per la majoria de la web

#Importacions
import reflex as rx
from tdr_web.styles.colors import Colors as colors


#Funció del botó
def link_button(title: str, body: str, url: str, disabled: bool = False) -> rx.Component: #Parametres
    return rx.link(
        rx.button(
            rx.hstack(
                #Icon de una fetxa
                rx.icon(
                    tag='arrow-big-right',
                    color='white'
                ),
                #Títol i text diferent en cada un
                rx.vstack(
                    rx.text(title, color='white', size='4'),
                    rx.text(body, color='white')
                ),
                width='580px',
                margin='1em',
                color='white',
            ),
            size='2', #Mida
            disabled=disabled, #Es pot triar si està deshabilitat
            radius='medium', #Radius
            background_color=colors.PRIMARY.value, #Color
        ),
        href=url, #Url del botó (Per si et porta a una altre pestanya)
    )