import reflex as rx
from tdr_web.styles.colors import Colors as colors


def navbar() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.link(
                'IE Josep Maria Xandri',
                href='/',
                color='white',
                align='center',
                justify='center',
                _hover = None,
            ),
            rx.hstack(
                rx.link(
                 rx.button(
                    'Afegir alumnes',
                    size='2',
                    color=colors.VERD.value,
                    background_color = 'white'
                ),
                 is_external=True,
                href='/add_student'
                ),
                rx.link(
                    rx.button(
                        'Modificar alumnes',
                        size='2',
                        color=colors.VERD.value,
                        background_color = 'white'
                    ),
                    is_external=True,
                    href='/modify_student'
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