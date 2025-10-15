import os
import subprocess
import google.generativeai as genai

class AIManager:
    """Manages AI and Git operations independent of the UI framework."""
    def __init__(self):
        self.api_key = None
        self.model = None

    def configure_api(self, api_key):
        """Configures the Gemini API with the provided key."""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.api_key = api_key
            # A quick test to validate the key
            self.model.generate_content("hello", generation_config=genai.types.GenerationConfig(max_output_tokens=5))
            return True, "API key configured successfully."
        except Exception as e:
            self.api_key = None
            self.model = None
            return False, f"Failed to configure API key: {e}"

    def has_api_key(self):
        """Checks if the API key is set."""
        return self.api_key is not None

    def get_ai_response(self, prompt, file_content):
        """Gets a modified code response from the Gemini API."""
        if not self.model:
            return None, "API key not configured."

        try:
            full_prompt = (
                "Based on the user's request, please modify the following Python code. "
                "Only return the complete, modified code. Do not include any explanations, "
                "markdown formatting, or other text outside of the code itself.\n\n"
                f"User Request: '{prompt}'\n\n"
                f"Original Code:\n```python\n{file_content}\n```"
            )
            response = self.model.generate_content(full_prompt)
            cleaned_response = self._clean_response(response.text)
            return cleaned_response, None
        except Exception as e:
            return None, f"An error occurred while communicating with the AI: {e}"

    @staticmethod
    def _clean_response(text):
        """Removes markdown code fences and other non-code text."""
        if text.strip().startswith("```python"):
            text = text.strip()[9:]
        if text.strip().endswith("```"):
            text = text.strip()[:-3]
        return text.strip()

    @staticmethod
    def list_files(directory_path, extension_filter=('.py', '.rst', '.toml', '.yml', '.md', '.cif')):
        """Lists files in a directory with optional extension filtering."""
        if not directory_path or not os.path.isdir(directory_path):
            return []
        files = []
        for file_name in os.listdir(directory_path):
            if file_name.endswith(extension_filter):
                files.append(file_name)
        return sorted(files)

    @staticmethod
    def read_file(file_path):
        """Reads the content of a file."""
        if file_path and os.path.isfile(file_path):
            with open(file_path, "r", encoding='utf-8') as file:
                return file.read()
        return None

    @staticmethod
    def save_file(file_path, content):
        """Saves content to a file."""
        if file_path:
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(content)
            return True
        return False

    @staticmethod
    def _run_git_command(command, cwd):
        """Executes a Git command in a specified directory."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
            )
            return True, result.stdout.strip() or "Success"
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
        except FileNotFoundError:
            return False, "Git command not found. Is Git installed and in your PATH?"

    def git_add(self, file_path):
        """Stages a file using 'git add'."""
        if not file_path:
            return False, "No file path provided."
        return self._run_git_command(["git", "add", file_path], os.path.dirname(file_path))

    def git_commit(self, file_path, message):
        """Commits a staged file with a message."""
        if not file_path:
            return False, "No file path provided."
        if not message:
            return False, "Commit message cannot be empty."
        add_success, add_msg = self.git_add(file_path)
        if not add_success:
            return False, f"Failed to stage file before commit: {add_msg}"
        return self._run_git_command(["git", "commit", "-m", message], os.path.dirname(file_path))

    def git_reset(self, file_path):
        """Resets a staged file from the index."""
        if not file_path:
            return False, "No file path provided."
        return self._run_git_command(["git", "reset", "HEAD", file_path], os.path.dirname(file_path))

    def git_checkout(self, file_path):
        """Discards changes in the working directory for a file."""
        if not file_path:
            return False, "No file path provided."
        return self._run_git_command(["git", "checkout", "--", file_path], os.path.dirname(file_path))
