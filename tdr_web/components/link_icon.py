import reflex as rx


def link_icon(url:str,forma:str,col:str) -> rx.Component:
    return rx.link(
        rx.icon(
            tag=forma,
            color = col
        ),
        href = url,
        is_external=True
    )