### Link button ###
#Fitxer amb una funció que crea un títol amb uns estils generals els quals seràn fets servir per la majoria de la web

#Importacions
import reflex as rx
from tdr_web.styles.colors import Colors as colors

#Funció principal
def title(text:str) -> rx.Component:
    #És una funció molt curta però m'asseguro de que tots els títols són iguals i m'estalvio de crear-ne un cada com
    return rx.heading(
        text,
        color = colors.VERD.value,
        margin_top = '0.9em'
    )