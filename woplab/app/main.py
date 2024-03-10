from flask import Flask


DEFAULT_PORT = 8080


app = Flask('woplab', instance_relative_config=True)
#app.config.from_object("config.cfg")

with app.app_context():
    from woplab.app import routes  # noqa: F401
    #from woplab.dash import dash_app1, dash_app2

    #app = dash_app1.init_dash(app)
    #app = dash_app2.init_dash(app)


if __name__ == "__main__":
    # for debugging while developing
    app.run(debug=True, port=DEFAULT_PORT)
