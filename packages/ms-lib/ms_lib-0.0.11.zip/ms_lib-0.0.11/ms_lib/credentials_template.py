
from storage_template import storage_template

from flask import request


class credentials_template(storage_template):

    #############################################
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = super(credentials_template, self).create_app()

        @app.route('/check', methods=['POST'])
        def check():
            data = request.get_json()
            return self.check(data)

        return app


    #############################################
    #             Module methods                #
    #############################################
    def check(self, data):
        return "Not found", 404

