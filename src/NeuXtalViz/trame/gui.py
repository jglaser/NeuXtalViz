import os
from pathlib import Path
import sys
from typing import Any

from trame_server.core import Server
from trame.ui.vuetify3 import SinglePageLayout

# Correctly import from the nova framework
from nova.mvvm.trame_binding import TrameBinding
from nova.trame import ThemedApp

# Import the new AI components
from NeuXtalViz.ai.manager import AIManager
from NeuXtalViz.trame.views import main_view, ai_assistant_panel

# Your original, correct application imports
from NeuXtalViz.models.volume_slicer import VolumeSlicerModel
from NeuXtalViz.view_models.volume_slicer import VolumeSlicerViewModel
from NeuXtalViz.trame.views.volume_slicer import VolumeSlicerView


class NeuXtalViz(ThemedApp):
    """Main view for NeuXtalViz."""

    def __init__(self, server: Server = None) -> None:
        super().__init__(server=server)
        
        binding = TrameBinding(self.server.state)
        self.view_model = VolumeSlicerViewModel(VolumeSlicerModel(), binding)
        
        self._setup_ai_assistant()
        self.ui = self._create_ui()

    def _create_ui(self):
        """Creates the main UI layout for the application."""
        with SinglePageLayout(self.server) as layout:
            layout.title.set_text("NeuXtalViz")
            layout.toolbar.add_child(main_view.create_main_view())

            with layout.content:
                # CORRECTED: Pass both the server and the view_model to the constructor.
                VolumeSlicerView(self.server, self.view_model)
                
                ai_assistant_panel.create_ai_assistant_panel()
        return layout

    def _setup_ai_assistant(self):
        """Initializes state and controllers for the AI Assistant."""
        state = self.server.state
        ctrl = self.server.controller

        self.ai_manager = AIManager()
        state.ai_dialog = False
        state.ai_api_key_dialog = False
        state.ai_api_key = ""
        state.ai_api_key_input = ""
        state.ai_file_list = []
        state.ai_current_file = ""
        state.ai_file_content = ""
        state.ai_prompt = ""
        self.PROJECT_ROOT = Path(__file__).resolve().parents[3]

        ctrl.ai_list_files = self._ai_list_files
        ctrl.ai_load_file = self._ai_load_file
        ctrl.ai_configure_api = self._ai_configure_api
        ctrl.ai_send_prompt = self._ai_send_prompt
        ctrl.ai_save_file = self._ai_save_file
        ctrl.ai_git_add = lambda: self._run_git_command("git_add")
        ctrl.ai_git_commit = lambda: self._run_git_command("git_commit")
        ctrl.ai_git_reset = lambda: self._run_git_command("git_reset")
        ctrl.ai_git_checkout = lambda: self._run_git_command("git_checkout")

        @self.server.state.change("trame__title")
        def check_api_key_on_startup(trame__title, **kwargs):
            if not self.ai_manager.has_api_key():
                state.ai_api_key_dialog = True

    def _ai_list_files(self):
        self.server.state.ai_file_list = self.ai_manager.list_files(self.PROJECT_ROOT)

    def _ai_load_file(self):
        if self.server.state.ai_current_file:
            full_path = os.path.join(self.PROJECT_ROOT, self.server.state.ai_current_file)
            content = self.ai_manager.read_file(full_path)
            self.server.state.ai_file_content = content if content is not None else ""

    def _ai_configure_api(self):
        success, message = self.ai_manager.configure_api(self.server.state.ai_api_key)
        if success:
            self.server.controller.js_notification("Success", message)
        else:
            self.server.controller.js_error("API Error", message)

    def _ai_send_prompt(self):
        if not self.ai_manager.has_api_key():
            self.server.controller.js_error("Error", "API Key not set.")
            return
        if not self.server.state.ai_current_file:
            self.server.controller.js_error("Error", "No file is selected.")
            return
        response, error = self.ai_manager.get_ai_response(self.server.state.ai_prompt, self.server.state.ai_file_content)
        if error:
            self.server.controller.js_error("AI Error", error)
        else:
            self.server.state.ai_file_content = response
            self.server.controller.js_notification("Success", "AI has updated the file content.")

    def _ai_save_file(self):
        if self.server.state.ai_current_file:
            full_path = os.path.join(self.PROJECT_ROOT, self.server.state.ai_current_file)
            if self.ai_manager.save_file(full_path, self.server.state.ai_file_content):
                self.server.controller.js_notification("Success", f"File '{self.server.state.ai_current_file}' saved.")
            else:
                self.server.controller.js_error("Error", "Failed to save file.")

    def _run_git_command(self, func_name):
        if self.server.state.ai_current_file:
            full_path = os.path.join(self.PROJECT_ROOT, self.server.state.ai_current_file)
            git_func = getattr(self.ai_manager, func_name)
            
            if func_name == "git_commit":
                commit_message = self.server.state.ai_prompt or f"AI change to {os.path.basename(self.server.state.ai_current_file)}"
                success, message = git_func(full_path, commit_message)
            else:
                success, message = git_func(full_path)
                
            if success:
                self.server.controller.js_.notification("Git", message)
                if func_name == "git_checkout":
                    self._ai_load_file()
            else:
                self.server.controller.js_error("Git Error", message)
        else:
            self.server.controller.js_error("Error", "No file selected for Git operation.")

def trame(server: Server = None, *args: Any, **kwargs: Any) -> None:
    """Entry point for running the Trame application."""
    app = NeuXtalViz(server)
    for arg in sys.argv[1:]:
        try:
            key, value = arg.split("=")
            kwargs[key] = int(value)
        except Exception:
            pass
    
    server_options = {
        "host": "0.0.0.0",
        "open_browser": False,
        "port": 8080,
        "timeout": 0,
        **kwargs,
    }
    app.server.start(**server_options)
