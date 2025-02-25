import reflex as rx
from tdr_web.styles.colors import Colors as colors


def link_button(title: str, body: str, url: str, disabled: bool = False) -> rx.Component:
    return rx.link(
        rx.button(
            rx.hstack(
                rx.icon(
                    tag='arrow-big-right',
                    color='white'
                ),
                rx.vstack(
                    rx.text(title, color='white', size='4'),
                    rx.text(body, color='white')
                ),
                width='580px',
                margin='1em',
                color='white',
            ),
            size='2',
            disabled=disabled,
            radius='medium',
            background_color=colors.PRIMARY.value,
        ),
        href=url,
        is_external=True
    )