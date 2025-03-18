### Navbar ###
#Funció que és cridada a totes les pàgines de la web

#Importacions
import reflex as rx
from tdr_web.styles.colors import Colors as colors


#Funció front-end
def navbar() -> rx.Component:
    #Importar dintre de la funció per evitar una importació circular
    from tdr_web.tdr_web import Verify
    #Variable per saber si l'usuari està autoritzat
    is_autenticated = Verify.user["Autoritzat"]
    return rx.box(
        rx.flex(
            rx.hstack(    
                #Link que et porta a la pàgina principal
                rx.link(
                    'IE Josep Maria Xandri',
                    href='/',
                    color='white',
                    align='center',
                    justify='center',
                    _hover = None,
                ),
            ),
            #Si està autoritzat mostrar els botons
            rx.cond(
                is_autenticated,
                rx.hstack(
                    #Botons
                    rx.link(
                    rx.button(
                        'Afegir alumnes',
                        size='2',
                        color=colors.VERD.value,
                        background_color = 'white'
                    ),
                    href='/add_student'
                    ),
                    rx.link(
                        rx.button(
                            'Modificar alumnes',
                            size='2',
                            color=colors.VERD.value,
                            background_color = 'white',
                        ),
                        href='/modify_student'
                    ),
                    rx.link(
                        rx.button(
                            'Afegir professors',
                            size='2',
                            color=colors.VERD.value,
                            background_color = 'white'
                        ),
                        href='/add_teacher'
                    ),rx.link(
                        rx.button(
                            'Modificar professors',
                            size='2',
                            color=colors.VERD.value,
                            background_color = 'white'
                        ),
                        href='/modify_users'
                    ),
                    #Avatar
                    rx.avatar(
                        fallback=Verify.user_input[0],
                        color_scheme="green",
                        size='3',
                        high_contrast=False,
                        variant="solid"
                    )
                ),
            ),
            #Avatar per si no està autoritzat
            rx.cond(
                ~ is_autenticated,
                rx.avatar(
                    fallback=Verify.user_input[0],
                    color_scheme="green",
                    high_contrast=False,
                    variant="solid"
                )
            ),
            #Parametres estetics
            position = 'fixed',
            bg = colors.PRIMARY.value,
            width = '100%',
            padding_x = '16px',
            padding_y = '8px',
            z_index = '100% !important',
            spacing='9',
            justify='between'
        )
    )

