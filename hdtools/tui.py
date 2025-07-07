from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static
from hdtools import client

class HDToolsApp(App):
    CSS_PATH = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search user...", id="search_input")
        yield Static(id="result_display")
        yield Footer()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        user = message.value.strip()
        result_widget = self.query_one("#result_display", Static)
        if user:
            try:
                result = client.search_user(user)
                result_widget.update(str(result))
            except Exception as e:
                result_widget.update(f"Error: {e}")

def run():
    app = HDToolsApp()
    app.run()
