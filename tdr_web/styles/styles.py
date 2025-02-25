import reflex as rx
from tdr_web.styles.colors import Colors as colors

BASE_STYLE = {
    'background_color': colors.BACKGROUND.value,
    'font_familly':'Geist',
    rx.button:{
        'backgroud_color': colors.SECONDARY.value,
        'width':'100%',
        'height':'100%',
        'display':'block',
        'padding':'0.5em',
        'text_color':colors.TEXT.value,
        '_hover':{
            'backgroud_color': colors.PRIMARY.value
        }
    },
    rx.link:{
        'text_decoration':'none',
        '_hover':{}
    },
    rx.text:{
        'color': colors.TEXT.value,
        'font_family': 'Geist',
    },
    rx.heading:{
        'color': colors.TEXT.value,
        'font_familly': 'Geist'
    },
    rx.link:{
        '_hover':{}
    }
}