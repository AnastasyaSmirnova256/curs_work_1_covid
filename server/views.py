import csv
import io
import sys
from datetime import datetime
from io import StringIO
from math import sqrt

import matplotlib
from matplotlib import pyplot as plt
from sanic import json, HTTPResponse
from sanic.request import Request
from sanic.views import HTTPMethodView
from db.intefrace import *
from utils.loggining import *
from peewee import fn


class PassDataCsv(HTTPMethodView):
    def post(self, request: Request):
        file_data: bytes = request.body
        f = StringIO(file_data.decode(sys.getdefaultencoding()))
        logger.debug("start processing")
        data = [i for i in csv.reader(f, delimiter=',')]
        headers = data.pop(0)
        data_source = []
        for dat in data:
            new_row = {}
            for h in headers:
                payload: str = dat[headers.index(h)]
                try:
                    payload_value = float(payload)
                except:
                    payload_value = payload
                if payload.count("-") == 2:
                    payload_value = datetime.strptime(payload, "%Y-%M-%d").date()
                new_row.update({h: payload_value})
            DataDbModel.create(**new_row)
        #     data_source.append(new_row)
        # logger.debug(f"data processed {len(data_source)}")
        # DataDbModel.insert_many(data_source).execute()

        return json({"status": "ok"})


class ContinentsList(HTTPMethodView):
    def get(self, request: Request):
        cnt_list = [i.continent for i in DataDbModel.select(DataDbModel.continent.distinct())]
        logger.debug(cnt_list)
        return json(cnt_list)


class GraphDeath(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            return json({"status": 'invalid json'})
        else:
            fetched_data = DataDbModel.select(DataDbModel.location,
                                              fn.SUM(DataDbModel.total_deaths).alias("death")).where(
                DataDbModel.continent == request.json["continent"]).group_by(
                DataDbModel.continent, DataDbModel.location).limit(5)
            logger.debug(fetched_data)
            x_values = [i.location for i in fetched_data]
            y_values = [i.death for i in fetched_data]
            matplotlib.pyplot.plot(x_values, y_values)
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="jpeg")
            resp = HTTPResponse()
            resp.body = img_buf.getvalue()
            resp.headers = {"content-type": "image/jpeg"}
            return resp


class GraphVac(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            return json({"status": 'invalid json'})
        else:
            fetched_data = DataDbModel.select(DataDbModel.location,
                                              (fn.SUM(DataDbModel.total_vaccinations)/fn.SUM(DataDbModel.population)*100).alias("vacs")).where(
                DataDbModel.continent == request.json["continent"]).group_by(
                DataDbModel.continent, DataDbModel.location).limit(5)
            logger.debug(fetched_data)
            x_values = [i.location for i in fetched_data]
            y_values = [i.vacs for i in fetched_data]
            matplotlib.pyplot.plot(x_values, y_values)
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="jpeg")
            resp = HTTPResponse()
            resp.body = img_buf.getvalue()
            resp.headers = {"content-type": "image/jpeg"}
            return resp


class ProcessDataPercent(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            return json({"status": 'invalid json'})
        else:
            '''
            json_body :  {"continent": " " , "percent": } 
            '''
            fetched_data = DataDbModel.select(DataDbModel.location, fn.SUM(DataDbModel.population),
                                              (fn.SUM(DataDbModel.total_vaccinations) / fn.SUM(
                                                  DataDbModel.population) * 100).alias("percent")).where(
                DataDbModel.continent == request.json["continent"]).group_by(DataDbModel.location)

            return json({"countries": [{i.location: i.percent} for i in fetched_data if
                                           (i.percent != None) and (i.percent > request.json["percent"])]})


class DeleteData(HTTPMethodView):
    def delete(self, request: Request):
        '''
        json_body : {"id":1254125}
        '''
        if not request.json:
            return json({"status": "invalid json"})
        if not request.json["id"]:
            return json({"status": "invalid id"})
        else:
            try:
                DataDbModel.delete_by_id(int(request.json["id"]))
                return json({"status": "ok"})
            except Exception as e:
                logger.warning(e)
                return json({"status": "invalid id"})

################################################################### Ann ###################################################################

class ProcessDataCorrel(HTTPMethodView):
    def formula(self, fetched_data):
        country_one = fetched_data[0]
        country_two = fetched_data[1]
        x = country_one.TC
        xi = country_one.TC / country_one.kol
        y = country_two.TC
        yi = country_two.TC / country_two.kol
        return ((x - xi) * (y - yi)) / sqrt(((x - xi) ** 2) * ((y - yi) ** 2))

    def get(self, request: Request):
        if not request.json.get("daterange"):
            '''
            json_body : {"country_one": "Spain", "country_two":"Sweden" }
            '''
            c1 = request.json["country_one"]
            c2 = request.json["country_two"]
            fetched_data = DataDbModel.select(DataDbModel.location,
                                              fn.SUM(DataDbModel.total_cases).alias("TC"),
                                              fn.Count(DataDbModel.iso_code).alias("kol")).where(
                (DataDbModel.location == c1) | (DataDbModel.location == c2)).group_by(
                DataDbModel.location).order_by(DataDbModel.location)
            logger.debug(fetched_data)
            logger.debug({"koeficent": self.formula(fetched_data)})
            return json({"koeficent": self.formula(fetched_data)})
        else:
            '''
            json_body : {"country_one": "Spain", "country_two":"Sweden", "daterange":{"from":"Y-M-d", "to":"Y-M-d"} }
            '''
            froms = datetime.strptime(request.json["daterange"]["from"], "%Y-%M-%d").date()
            to = datetime.strptime(request.json["daterange"]["to"], "%Y-%M-%d").date()
            c1 = request.json["country_one"]

            c2 = request.json["country_two"]

            fetched_data = DataDbModel.select(DataDbModel.location,
                                              fn.SUM(DataDbModel.total_cases).alias("TC"),
                                              fn.Count(DataDbModel.iso_code).alias("kol")).where(
                (DataDbModel.location == c1) | (DataDbModel.location == c2) & DataDbModel.date.between(froms,
                                                                                                       to)).group_by(
                DataDbModel.location).order_by(DataDbModel.location)
            logger.debug(fetched_data)
            logger.debug(self.formula(fetched_data))
            return json({"koeficent": self.formula(fetched_data)})


class ProcessDataTopDeath(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            '''
            json_body : 
            '''
            fetched_data = DataDbModel.select(DataDbModel,
                                              fn.SUM(DataDbModel.total_deaths_per_million).alias("total")).group_by(
                DataDbModel.location).limit(10).order_by(fn.SUM(DataDbModel.total_deaths_per_million).desc())
            logger.debug(fetched_data)
            return json({"country's top": [{i.location: i.total} for i in fetched_data]})
        else:
            '''
            json_body : {"from":"Y-M-d", "to":"Y-M-d"}
            '''
            froms = datetime.strptime(request.json["from"], "%Y-%M-%d").date()
            to = datetime.strptime(request.json["to"], "%Y-%M-%d").date()
            fetched_data = DataDbModel.select(DataDbModel,
                                              fn.SUM(DataDbModel.total_deaths_per_million).alias("total")).where(
                DataDbModel.date.between(froms, to)).group_by(
                DataDbModel.location).limit(10).order_by(fn.SUM(DataDbModel.total_deaths_per_million).desc())
            logger.debug(f"from: {froms}, to: {to}")
            logger.debug(fetched_data)
            logger.debug({"country's top": [{i.location: i.total} for i in fetched_data]})
            return json({"country's top": [{i.location: i.total} for i in fetched_data]})


################################################################### Kirill ###################################################################

class ContriesList(HTTPMethodView):
    def get(self, request: Request):
        cnt_list = [i.location for i in DataDbModel.select(DataDbModel.location.distinct())]
        logger.debug(cnt_list)
        return json(cnt_list)


class GraphDeathPercent(HTTPMethodView):

    def get(self, request: Request):

        if not request.json:
            return json({"status": "invalid json"})
        else:
            if not request.json.get("country"):
                return json({"status": "invalid json"})
            else:
                fetched_data = DataDbModel.select(DataDbModel.date, DataDbModel.location,
                                                  ((DataDbModel.total_deaths / DataDbModel.total_cases) * 100).alias(
                                                      "pecent")).where(
                    DataDbModel.location == request.json["country"]).group_by(DataDbModel.date).order_by(
                    DataDbModel.date)
                logger.debug(fetched_data)
                x_values = [i.date for i in fetched_data]
                y_values = [i.pecent for i in fetched_data]
                dates = matplotlib.dates.date2num(x_values)
                matplotlib.pyplot.plot_date(dates, y_values)
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format="jpeg")
                resp = HTTPResponse()
                resp.body = img_buf.getvalue()
                resp.headers = {"content-type": "image/jpeg"}
                return resp


class ProcessDataTopVac(HTTPMethodView):
    def get(self, request: Request):

        if not request.json:
            '''
            json_body : 
            '''
            fetched_data = DataDbModel.select(DataDbModel,
                                              fn.SUM(DataDbModel.total_vaccinations).alias("total")).group_by(
                DataDbModel.location).limit(10).order_by(fn.SUM(DataDbModel.total_vaccinations).desc())
            logger.debug(fetched_data)
            return json({"country's top": [{i.location: i.total} for i in fetched_data]})
        else:
            '''
            json_body : {"from":"Y-M-d", "to":"Y-M-d"}
            '''
            froms = datetime.strptime(request.json["from"], "%Y-%M-%d").date()
            to = datetime.strptime(request.json["to"], "%Y-%M-%d").date()
            fetched_data = DataDbModel.select(DataDbModel,
                                              fn.SUM(DataDbModel.total_vaccinations).alias("total")).where(
                DataDbModel.date.between(froms, to)).group_by(
                DataDbModel.location).limit(10).order_by(fn.SUM(DataDbModel.total_vaccinations).desc())
            logger.debug(f"from: {froms}, to: {to}")
            logger.debug(fetched_data)
            logger.debug({"country's top": [{i.location: i.total} for i in fetched_data]})
            return json({"country's top": [{i.location: i.total} for i in fetched_data]})