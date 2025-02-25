import reflex as rx
from tdr_web.styles.colors import Colors as colors

def title(text:str) -> rx.Component:
    return rx.heading(text, color = colors.VERD.value, margin_top = '0.9em')