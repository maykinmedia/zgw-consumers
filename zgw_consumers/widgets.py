from django.forms.widgets import Textarea

from privates.widgets import PrivateFileWidget


class NoDownloadPrivateFileWidget(PrivateFileWidget):
    template_name = "admin/widgets/clearable_no_download_private_file_input.html"


class PasswordAreaWidget(Textarea):
    def __init__(self, attrs=None, render_value=False):
        super().__init__(attrs)
        self.render_value = render_value

    def get_context(self, name, value, attrs):
        if not self.render_value:
            value = None
        return super().get_context(name, value, attrs)
