"""App module to demo authentication with supabase."""
# 9dg08MVzIfI3ZcuH

import reflex as rx
import supabase
import os

from .base_state import State
from .registration import registration_page as registration_page
from .login import require_login
from .checkin_user import checkinpage as checkinpage
from dotenv import load_dotenv
from .css import style

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client = supabase.Client(supabase_url, supabase_key)

def loggin_button(name, href):
    return rx.link(
        rx.icon(tag="lock", mr=2),
        name,
        display="inline-flex",
        align_items="center",
        py=3,
        px=6,
        href=href,
        border="1px solid #eaeaea",
        color="#eaeaea",
        font_weight="semibold",
        border_radius="full",
    )
    
def register_button(name, href):
    return rx.link(
        rx.icon(tag="email", mr=2),
        name,
        display="inline-flex",
        align_items="center",
        py=3,
        px=6,
        href=href,
        border="1px solid #eaeaea",
        color="#eaeaea",
        font_weight="semibold",
        border_radius="full",
    )
    
def checkin_button(name, href):
    return rx.link(
        rx.icon(tag="external_link", mr=2),
        name,
        display="inline-flex",
        align_items="center",
        py=3,
        px=6,
        href=href,
        border="1px solid #eaeaea",
        color="#eaeaea",
        font_weight="semibold",
        border_radius="full",
    )
    
def logout_button(name):
    return rx.link(
        rx.icon(tag="close", mr=2),
        name,
        display="inline-flex",
        align_items="center",
        py=3,
        px=6,
        on_click=State.do_logout,
        border="1px solid #eaeaea",
        color="#eaeaea",
        font_weight="semibold",
        border_radius="full",
    )

def index() -> rx.Component:
    return rx.fragment(
        rx.vstack(
            rx.heading("Sistema de Reconocimiento Facial", style=style.main_title),
            rx.color_mode_button(rx.color_mode_icon(), float="right", position="absolute", top="1em", right="1em"),
            rx.hstack(
                rx.cond(
                    State.is_hydrated & ~State.is_authenticated,
                    loggin_button("Register", "/register"),
                ),
                rx.cond(
                    State.is_hydrated & ~State.is_authenticated,
                    register_button("Login", "/login"),
                ),
                rx.cond(
                    State.is_hydrated & State.is_authenticated,
                    checkin_button("CheckIn", "/checkinpage"),
                ),
                rx.cond(
                    State.is_hydrated & State.is_authenticated,
                    logout_button("Logout"),
                ),
                spacing="1.5em",
                padding_top="10%",
            ),
            style=style.mainbox,
            background="url(background.svg)",
            background_repeat="repeat",
        ),
    )

# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.add_page(checkinpage)
app.compile()
