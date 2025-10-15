# Use vuetify3 to match the rest of the application
from trame.widgets import vuetify3 as vuetify

def create_main_view():
    """This function is only responsible for creating the app bar."""
    with vuetify.VAppBar(app=True, dense=True):
        vuetify.VToolbarTitle("NeuXtalViz")
        vuetify.VSpacer()
        vuetify.VBtn(
            "AI Assistant",
            icon=True,
            click="ai_dialog = !ai_dialog; trigger('ai_list_files');"
        )
