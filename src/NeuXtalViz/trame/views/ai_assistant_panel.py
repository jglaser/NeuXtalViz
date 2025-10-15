# Use vuetify3 to match the rest of the application
from trame.widgets import vuetify3 as vuetify

def create_ai_assistant_panel():
    """Creates the UI for the AI Assistant as a Trame dialog."""
    with vuetify.VDialog(
        v_model=("ai_dialog", False),
        persistent=True,
        max_width="80vw",
        scrollable=True,
    ) as dialog:
        with vuetify.VCard():
            vuetify.VCardTitle("AI Assistant")
            vuetify.VDivider()
            with vuetify.VCardText(style="height: 70vh;"):
                with vuetify.VRow(classes="fill-height"):
                    with vuetify.VCol(cols=3):
                        vuetify.VCardSubtitle("Files")
                        with vuetify.VList(dense=True, style="height: 95%; overflow-y: auto;"):
                            with vuetify.VListItem(
                                v_for="(item, i) in ai_file_list",
                                key="i",
                                click="ai_current_file = item; trigger('ai_load_file');",
                                active=("ai_current_file == item",),
                                color="primary",
                            ):
                                vuetify.VListItemTitle("{{ item }}")
                    with vuetify.VCol(cols=9, classes="d-flex flex-column"):
                        vuetify.VTextField(v_model="ai_current_file", readonly=True, dense=True, hide_details=True)
                        vuetify.VTextarea(v_model=("ai_file_content", ""), label="File Content", rows=15, auto_grow=True, outlined=True, spellcheck="false", classes="flex-grow-1")
                        vuetify.VTextarea(v_model=("ai_prompt", ""), label="Describe the changes you want to make...", rows=3, auto_grow=True, outlined=True)
            vuetify.VDivider()
            with vuetify.VCardActions():
                vuetify.VBtn("Set API Key", click="ai_api_key_dialog = true", small=True)
                vuetify.VSpacer()
                vuetify.VBtn("Send to AI", click="trigger('ai_send_prompt')", color="primary")
                vuetify.VBtn("Save", click="trigger('ai_save_file')")
                vuetify.VSpacer()
                with vuetify.VBtnToggle(dense=True):
                    vuetify.VBtn("Git Add", click="trigger('ai_git_add')")
                    vuetify.VBtn("Git Commit", click="trigger('ai_git_commit')")
                    vuetify.VBtn("Git Reset", click="trigger('ai_git_reset')")
                    vuetify.VBtn("Git Checkout", click="trigger('ai_git_checkout')")
                vuetify.VSpacer()
                vuetify.VBtn("Close", click="ai_dialog = false")

    with vuetify.VDialog(v_model=("ai_api_key_dialog", False), persistent=True, max_width="500px"):
        with vuetify.VCard():
            vuetify.VCardTitle("Set Gemini API Key")
            with vuetify.VCardText():
                vuetify.VTextField(label="API Key", v_model=("ai_api_key_input", ""), type="password")
            with vuetify.VCardActions():
                vuetify.VSpacer()
                vuetify.VBtn("Cancel", click="ai_api_key_dialog = false")
                vuetify.VBtn(
                    "Confirm",
                    color="primary",
                    click="ai_api_key = ai_api_key_input; ai_api_key_dialog = false; trigger('ai_configure_api');",
                )
    return dialog
