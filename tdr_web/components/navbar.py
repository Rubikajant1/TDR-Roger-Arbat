import reflex as rx
from tdr_web.styles.colors import Colors as colors
from db.db_client import db


def navbar() -> rx.Component:
    from tdr_web.tdr_web import Verify
    is_autenticated = Verify.user["Autoritzat"]
    return rx.box(
        rx.flex(
            rx.hstack(
                    
                rx.link(
                    'IE Josep Maria Xandri',
                    href='/',
                    color='white',
                    align='center',
                    justify='center',
                    _hover = None,
                ),
            ),
            rx.cond(
                is_autenticated,
                rx.hstack(
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
                    rx.avatar(
                        fallback=Verify.user_input[0],
                        color_scheme="green",
                        size='3',
                        high_contrast=False,
                        variant="solid"
                    )
                ),
            ),
            rx.cond(
                ~ is_autenticated,
                rx.avatar(
                    fallback=Verify.user_input[0],
                    color_scheme="green",
                    high_contrast=False,
                    variant="solid"
                )
            ),
        
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