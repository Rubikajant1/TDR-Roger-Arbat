### Link button ###
#Fitxer amb una funció que crea un icon amb uns estils generals els quals seràn fets servir per la majoria de la web

#Importacions
import reflex as rx


#Funció principal
def link_icon(url:str,forma:str,col:str) -> rx.Component: #Parametres
    return rx.link(
        #Icon
        rx.icon(
            tag=forma,
            color = col
        ),
        #Url
        href = url,
        is_external=False
    )