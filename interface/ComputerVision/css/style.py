STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Concert+One&display=swap",
    "https://fonts.googleapis.com/css2?family=Mina:wght@400;700&display=swap",
]

COURIER = "Courier New"
COURGETTE = "Courgette"
MINA = "Mina"
RUSSO_ONE = "Russo One"

shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"

form_style = dict(
    padding="2em",
    border_radius="5px",
    margin_y="0.5em",
    box_shadow=shadow,
    width="50vw",
    display="inline-block",
    border="1px solid #eaeaea"
)

inputs_style = dict(
    border="1px solid #0e0e0e",
    padding="0.5em",
    margin_y="0.5em",
    font_family=COURIER,
    color="#0e0e0e",
    background="#eaeaea"
)

button_style = dict(
    padding="1em", 
    width="100%", 
    margin_y="1em",
    font_family=COURIER,
)

mainbox = dict(
    display="flex",
    align_items="center",
    height="100vh",
    justify_content="center",
)

__next = dict (
    background="url(background.svg)",
    background_size="cover",
)

main_title = dict(
    font_family=COURIER,
    margin="0",
    padding="0",
    color="#aeaeae",
)