from sanic.app import Sanic
from sanic_cors import CORS

from server.views import *
from utils.loggining import setup_loggers


class Server:
    def __init__(self):
        self.sanic_app = Sanic("class_views_example")
        CORS(self.sanic_app)
        setup_loggers()
        self.register_api()

    def register_api(self):
        self.sanic_app.add_route(PassDataCsv.as_view(), "/data")
        self.sanic_app.add_route(GrapthDeath.as_view(), "/grapth_death")
        self.sanic_app.add_route(GrapthVac.as_view(), "/grapth_vac")

        self.sanic_app.add_route(ProcessDataSecond.as_view(), "/percent")
        self.sanic_app.add_route(DeleteData.as_view(), "/delete")
        self.sanic_app.add_route(ContsList.as_view(), "/continents")

    def run(self):
        self.sanic_app.run("0.0.0.0")
