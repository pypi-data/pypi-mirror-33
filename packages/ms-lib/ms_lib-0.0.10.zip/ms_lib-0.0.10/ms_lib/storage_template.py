import json
import jsonschema
import requests

from flask import Flask, request
from base_template import base_template


class storage_template(base_template):

    #############################################
    #             Initial config                #
    #############################################
    def __init__(self, network_config, schema_url, storage_config):

        self.schema = self.load_schema(schema_url)
        self.storage = self.create_storage(storage_config)

        app = self.create_app(debug=True)
        self.run(app, network_config)


    #############################################
    #               Load schemas                #
    #############################################
    def load_schema(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            exit(1)



    #############################################
    #           Set up the storage              #
    #############################################
    def create_storage(self, storage_config):
        if storage_config['type'] == 'mongodb':
            from storage import mongodb
            storage = mongodb(storage_config)
            return storage
        else:
            exit(1)



    #############################################
    #                   Routes                  #
    #############################################
    def create_app(self, debug=False):
        app = super(storage_template, self).create_app()

        @app.route('/<id>', methods=['GET'])
        def get(id):
            queries = request.args
            return self.get(id, queries)

        @app.route('/', methods=['GET'])
        def search():
            queries = request.args
            return self.search(queries)

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
        resources = self.storage.load({'id': id})
        if len(resources) == 1:
            data = resources[0]['data']
            return json.dumps(data), 200
        else:
            return "El recurso no existe", 404


    def search(self, queries):
        filter = {}
        for key in queries:
            value = queries[key]
            filter['data.' + key] = value

        resources = self.storage.load(filter)

        bundle = {}
        for resource in resources:
            bundle[resource['id']] = resource['data']

        return json.dumps(bundle)


    def create(self, queries, data):
        # Creamos un id
        id = self.id_generator()
        while len(self.storage.load({'id': id})) != 0:
            id = self.id_generator()

        # Validamos la informacion recivida frente al esquema
        try:
            jsonschema.validate(data, self.schema)
        except:
            return "El resurso no cumple con el esquema", 400

        # El anadimos el sujeto y lo almacenamos
        resource = {'id': id, 'data': data}
        r = self.storage.create(resource)
        if r:
            return id, 201
        else:
            return 'Ups algo ha ido mal', 400


    def update(self, id, queries, data):
        # Validamos la informacion recivida frente al esquema
        try:
            jsonschema.validate(data, self.schema)
        except:
            return "El resurso no cumple con el esquema", 400

        # Lo almacenamos
        resource = {'id': id, 'data': data}
        r = self.storage.update({'id': id}, resource, upsert=True)
        if r:
            return 'Success!', 201
        else:
            return 'Ups algo ha ido mal', 400



    def delete(self, id, queries):
        r = self.storage.delete({'id': id})
        if r > 0:
            return 'Success'
        else:
            return "No se ha podido eliminar el resurso solicitado", 404




    # Forzando a que el recurso existiese previamente
    # def update(self, id, new_data):
    #     # Verificamos que existe
    #     resources = self.storage.load({'id': id})
    #     if len(resources) == 1:
    #         data = resources[0]['data']
    #
    #         # Lo actualizamos con la informacion recivida
    #         try:
    #             data.update(new_data)
    #             jsonschema.validate(data, self.schema)
    #         except:
    #             return "El resurso no cumple con el esquema", 400
    #
    #         # Lo almacenamos
    #         resource = {'id': id, 'data': data}
    #         r = self.storage.update({'id': id}, resource)
    #         if r:
    #             return 'Success!', 201
    #         else:
    #             return 'Ups algo ha ido mal', 400
    #
    #     else:
    #         return "El recurso no existe", 404


