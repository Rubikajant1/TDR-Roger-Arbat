import reflex as rx
import hashlib
from tdr_web.components.navbar import navbar
from tdr_web.styles.colors import Colors as colors
from tdr_web.components.header import header
from tdr_web.styles.styles import BASE_STYLE
from tdr_web.components.primer import primer, AlumneState1r
from tdr_web.components.segon import segon, AlumneState2n
from tdr_web.components.tercer import tercer, AlumneState3r
from tdr_web.components.quart import quart, AlumneState4t
from tdr_web.components.add_students import afegir_alumnes
from tdr_web.components.modify_student import modificar_alumne, AlumnState


config = rx.Config(
    app_name='Web TDR',
    frontend_port=3000
)


CORRECT_PASSWORD = "tdrarbat0123"

class Verify(rx.State):
    is_authenticated: bool = False
    password_input: str = ""
    show_error: bool = False

    def check_password(self):
        hashed_input = hashlib.sha256(self.password_input.encode()).hexdigest()
        hashed_correct = hashlib.sha256(CORRECT_PASSWORD.encode()).hexdigest()

        if hashed_input == hashed_correct:
            self.is_authenticated = True
            self.show_error = False
        else:
            self.is_authenticated = False
            self.show_error = True
            self.password_input = ""

    def logout(self):
        self.is_authenticated = False
    
    def autenticar(self):
        self.is_authenticated = True

def login_page() -> rx.Component:
    return rx.box(
        rx.box(
            rx.flex(
                rx.text("Gestió d'estudiants de l'IE Josep Maria Xandri",color='white',size='4'),
                rx.text("By Roger Arbat Juventeny",color='white'),
                position = 'fixed',
                bg = colors.PRIMARY.value,
                width = '100%',
                padding_x = '16px',
                padding_y = '8px',
                z_index = '100% !important',
                spacing='9',
                justify='between'
            )
        ),
        rx.vstack(
            rx.icon('lock-keyhole',color = colors.VERD.value,size=40),
            rx.heading("Accés restringit", size="7",color=colors.VERD.value),
            rx.text("Siusplau, posa la contrassenya per entrar"),
            rx.hstack(
                rx.input(
                    placeholder="Contrasenya",
                    type="password",
                    value=Verify.password_input,
                    on_change=Verify.set_password_input,
                    width='100%'
                ),
                rx.button(
                    "Entrar", 
                    on_click=Verify.check_password,
                    color_scheme="blue",
                    width = '40%',
                    height = '100%',
                    background_color = colors.PRIMARY.value
                )
            ),
            rx.cond(
                Verify.show_error,
                rx.text("Contraseña incorrecta", color="red")
            ),
            spacing="4",
            align="center",
            height="100vh",
            justify="center"
        ),
    )
    
def protected_content() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                header(),
                max_width='600px',
                width='100%',
                height = '100vh',
                margin='1em'
            ),
            margin_bottom='14em'
        ),
        spacing="4"
    )

def protected_page(route: str):
    # Función para páginas protegidas
    @rx.route
    def page():
        # Verificar acceso antes de renderizar
        access_check = Verify.check_access(route)
        if access_check:
            return access_check
        
        return rx.vstack(
            rx.text(f"Contenido protegido de {route}"),
            rx.button("Cerrar Sesión", on_click=Verify.logout)
        )
    return page


def index() -> rx.Component:
    return rx.cond(
        Verify.is_authenticated,
        protected_content(),
        login_page()
    )
    
app = rx.App(
        style=BASE_STYLE
    )

app.add_page(
    index,
    title='Web TDR',
    route='/',
    description="Gestió d'estudiants i d'assistencia de l'IE Josep Maria Xandri"
),
app.add_page(primer,route='/primer', title='Primer', on_load=AlumneState1r.initial_load)
app.add_page(segon,route='/segon', title='Segon', on_load=AlumneState2n.initial_load)
app.add_page(tercer,route='/tercer', title='Tercer', on_load=AlumneState3r.initial_load)
app.add_page(quart,route='/quart', title='Quart', on_load=AlumneState4t.initial_load)
app.add_page(afegir_alumnes,route='/add_student',title='Afegir alumnes')
app.add_page(modificar_alumne,route='/modify_student',title='Modificar alumnes',on_load=AlumnState.load_alumnes)