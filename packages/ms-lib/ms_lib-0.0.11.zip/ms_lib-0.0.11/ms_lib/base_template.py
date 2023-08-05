from flask import Flask


class base_template(object):

    #############################################
    #             Initial config                #
    #############################################
    def __init__(self, network_config):

        app = self.create_app(debug=True)
        self.run(app, network_config)



    #############################################
    #               Aux functions               #
    #############################################
    import string
    def id_generator(self, size=16, chars=string.ascii_lowercase + string.digits):
        import random
        return ''.join(random.choice(chars) for _ in range(size))



    #############################################
    #               Create the app              #
    #############################################
    def create_app(self, debug=False):
        app = Flask(__name__)
        app.debug = debug

        return app


    #############################################
    #                Start the app              #
    #############################################
    def run(self, app, network_config):

        if network_config.has_key('ssl'):
            app.run(host=network_config['addr'], port=network_config['port'], threaded=True,
                    ssl_context=(network_config['ssl']['cert'], network_config['ssl']['key']))
        else:
            app.run(host=network_config['addr'], port=network_config['port'], threaded=True)