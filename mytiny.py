#!/usr/bin/python
#coding:utf-8
import tornado.ioloop
import tornado.web
from tornado import web,gen,httpclient
import redis
import io
import tinify
from PIL import Image
tinify.key = "F0ztVDNuNsro1OnVuLYY2Z5Hwhv2507C"
pool = redis.ConnectionPool(host="192.168.0.27",port=6379,password='Hs123#',db=2)
r = redis.Redis(connection_pool=pool)
class Handler(tornado.web.RequestHandler):
    @gen.coroutine
    def conv(self,response):
        tmpIm = io.BytesIO(response.body)
        tmpImres = io.BytesIO()
        img = Image.open(io.BytesIO(response.body))
        picfmt=img.format
        if picfmt !='GIF':
            source = tinify.from_file(tmpIm)
            source.to_file(tmpImres)
            path = self.get_argument('url0')
            res=r.set(path,tmpImres.getvalue())
            res=r.get(path)
        else:
            res=tmpIm.getvalue()
        self.set_header("Content-type", "image/"+picfmt)
        self.finish(res)     
    @gen.coroutine
    def get(self):
        path = self.get_argument('url0')
        res=r.get(path)
        if res != None:
            self.set_header("Content-type", "image/png")
            self.set_header("imgcdn-status", "HIT")
            self.write(res)
        else:
            http = httpclient.AsyncHTTPClient()
            yield http.fetch(path,self.conv)
def make_app():
    return tornado.web.Application([
        (r"/", Handler),
    ])
if __name__ == "__main__":
    app = make_app()
    app.listen(88)
    tornado.ioloop.IOLoop.current().start()
