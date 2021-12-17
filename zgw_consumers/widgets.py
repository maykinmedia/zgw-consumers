from privates.widgets import PrivateFileWidget


class NoDownloadPrivateFileWidget(PrivateFileWidget):
    template_name = "admin/widgets/clearable_no_download_private_file_input.html"
