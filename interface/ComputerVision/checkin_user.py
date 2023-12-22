"""New user registration form and validation logic."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import reflex as rx
from fastapi import UploadFile
from .base_state import State
from .login import LOGIN_ROUTE, CHECKIN_ROUTE
from .login import require_login

import supabase
from dotenv import load_dotenv
from .css import style
import firebase_admin
from firebase_admin import credentials, db, storage
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")
storage_url = os.getenv("STORAGE_URL")

cred = credentials.Certificate("./ComputerVision/config/database/secret_key_example.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": database_url,
        "storageBucket": storage_url,
    },
)

ref = db.reference("Employees")

class CheckinState(State):
    """Handle registration form submission and redirect to login page after registration."""

    success: bool = False
    error_message: str = ""

    is_loading: bool = False
    img: list[str]

    async def handle_checkin(self, form_data) -> AsyncGenerator[rx.event.EventSpec | list[rx.event.EventSpec] | None, None]:
        """Handle registration form on_submit."""
        self.is_loading = True
        yield

        id = form_data.get("id")
        name = form_data.get("name")
        position = form_data.get("position")
        department = form_data.get("department")

        if not id:
            self.error_message = "El ID no puede estar vacío."
            rx.set_focus("id")
            self.is_loading = False
            yield
            return

        if not name:
            self.error_message = "El nombre no puede estar vacío."
            rx.set_focus("name")
            self.is_loading = False
            yield
            return

        if not position:
            self.error_message = "El cargo no puede estar vacío."
            rx.set_focus("position")
            self.is_loading = False
            yield
            return

        if not department:
            self.error_message = "El departamento de trabajo no puede estar vacío."
            rx.set_focus("department")
            self.is_loading = False
            yield
            return
        
        img = form_data.get("img")

        data = {
            id: {
                "name": name,
                "position": position,
                "department": department,
                "last_attendance": "2020-01-01 00:00:00",
                "total_attendance": 0,
            }
        }

        for key, value in data.items():
            ref.child(key).set(value)

        self.error_message = ""
        self.success = True
        self.is_loading = False
        yield
        await asyncio.sleep(3)
        yield [rx.redirect(CHECKIN_ROUTE), CheckinState.set_success(False)]

@require_login
@rx.page(route=CHECKIN_ROUTE)
def checkinpage() -> rx.Component:
    """Render the registration page."""
    color = "rgb(107,99,246)"
    register_form = rx.form(
        rx.input(placeholder="ID", id="id", style=style.inputs_style),
        rx.input(placeholder="Nombre", id="name", style=style.inputs_style),
        rx.input(placeholder="Cargo", id="position", style=style.inputs_style),
        rx.input(placeholder="Departamento", id="department", style=style.inputs_style),
        rx.input(placeholder="Imagen", id="img", type_="file", style=style.inputs_style),
        rx.button("Register", type_="submit", is_loading=CheckinState.is_loading, style=style.button_style),
        style=style.form_style,
        on_submit=CheckinState.handle_checkin
    )
    return rx.fragment(
        rx.cond(
            CheckinState.success,
            rx.vstack(
                rx.text("Registro Exitoso!, Ya puedes asistir al evento programado"),
                rx.spinner(),
            ),
            rx.vstack(
                rx.cond(
                    CheckinState.error_message != "",
                    rx.text(CheckinState.error_message),
                ),
                register_form,
                rx.link("Checking", href=CHECKIN_ROUTE, color="#aeaeae"),
                padding_top="10vh",
                background="url(../background.svg)",
                background_repeat="repeat",
                height="100vh"
            ),
        )
    )
