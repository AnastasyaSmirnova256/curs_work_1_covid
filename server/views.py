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


class ContsList(HTTPMethodView):
    def get(self, request: Request):
        cnt_list = [i.continent for i in DataDbModel.select(DataDbModel.continent.distinct())]
        logger.debug(cnt_list)
        return json(cnt_list)


class GrapthDeath(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            return json({"status": 'invalid json'})
        else:
            fetched_data = DataDbModel.select(DataDbModel.location,
                                              fn.SUM(DataDbModel.total_deaths).alias("death")).where(
                DataDbModel.continent == request.json["continent"]).group_by(
                DataDbModel.continent, DataDbModel.location)
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


class GrapthVac(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            return json({"status": 'invalid json'})
        else:
            fetched_data = DataDbModel.select(DataDbModel.location,
                                              (fn.SUM(DataDbModel.total_vaccinations)/fn.SUM(DataDbModel.population)*100).alias("vacs")).where(
                DataDbModel.continent == request.json["continent"]).group_by(
                DataDbModel.continent, DataDbModel.location)
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


class ProcessDataSecond(HTTPMethodView):
    def get(self, request: Request):
        if not request.json:
            return json({"status": 'invalid json'})
        else:
            '''
            json_body :  {"continent": " " , "percent" } 
            '''
            fetched_data = DataDbModel.select(DataDbModel.location, fn.SUM(DataDbModel.population),
                                              (fn.SUM(DataDbModel.total_vaccinations) / fn.SUM(
                                                  DataDbModel.population) * 100).alias("percent")).where(
                DataDbModel.continent == request.json["continent"]).group_by(DataDbModel.location)

            return json({"country's top": [{i.location: i.percent} for i in fetched_data if
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
