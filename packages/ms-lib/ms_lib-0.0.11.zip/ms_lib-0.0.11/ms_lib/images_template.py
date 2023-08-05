from base_template import base_template

from flask import send_file
import os

class images_template(base_template):


    #############################################
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = super(backend_template, self).create_app()

        @app.route('/<id>', methods=['GET'])
        def get(id):
            queries = request.args
            return self.get(id, queries)

        @app.route('/', methods=['POST'])
        def create():
            queries = request.args
            data = request.get_json()
            return self.create(queries, data)

        @app.route('/<id>', methods=['PUT'])
        def update(id):
            queries = request.args
            data = request.get_json()
            return self.update(id, queries, data)

        @app.route('/<id>', methods=['DELETE'])
        def delete(id):
            queries = request.args
            return self.delete(id, queries)

        return app


    #############################################
    #             Module methods                #
    #############################################
    def get(self, id, queries):
        try:
            return send_file(os.getcwd() + "/images/" + id + ".png", mimetype='image/png'), 200
        except:
            return "El fichero no existe o todavia no esta listo", 404



    def create(self, queries, data):
        # Get id from parent
        id = self.id_generator()

        # Start the image
        self.create_image(id, queries, data)

        return id, 201



    def create_image(self, id, queries, data):
        # pyplot.savefig('images' + id + '.png', dpi=300)
        pass


