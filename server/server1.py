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
        self.sanic_app.add_route(PassDataCsv.as_view(), "/events/covid/data")
        self.sanic_app.add_route(GraphDeath.as_view(), "/events/covid/graph_death")
        self.sanic_app.add_route(GraphVac.as_view(), "/events/covid/graph_vac")

        self.sanic_app.add_route(ProcessDataPercent.as_view(), "/events/covid/percent")
        self.sanic_app.add_route(DeleteData.as_view(), "/events/covid/delete")
        self.sanic_app.add_route(ContinentsList.as_view(), "/events/covid/continents")

        #Ann
        self.sanic_app.add_route(ProcessDataCorrel.as_view(), "/events/covid/correlation")
        self.sanic_app.add_route(ProcessDataTopDeath.as_view(), "/events/covid/top_death")
        #Kirill
        self.sanic_app.add_route(GraphDeathPercent.as_view(), "/events/covid/graph_death_percent")
        self.sanic_app.add_route(ProcessDataTopVac.as_view(), "/events/covid/top_vac")
        self.sanic_app.add_route(ContriesList.as_view(), "/events/covid/countries")

    def run(self):
        self.sanic_app.run("0.0.0.0")
