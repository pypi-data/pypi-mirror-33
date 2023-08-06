from flask import send_file


class FileDownloadEnterpriseApi:

    def __init__(self, fh):
        self.fh = fh

    def response(self, filename=None):
        return send_file(
            self.fh,
            as_attachment=True,
            attachment_filename=filename
        )
