from flask import Flask
from flask_restful import Resource, Api
import os

from Segmentation.slice import sliceEvent
from Translate.Translate import translate

app = Flask(__name__)
api = Api(app)

app_file_dir = 'com.example.myfristandroid/'


class GetFileNames(Resource):
    def get(self, file_dir):
        result = os.listdir('Preprocessing/' + file_dir)
        return {'fileNames': result}


class GetFileContent(Resource):
    def get(self, file_dir):
        file_dir = 'Preprocessing/' + file_dir
        with open(file_dir) as f:
            return {'fileContent': f.read()}


class SliceEvent(Resource):
    def get(self, file_dir):
        return sliceEvent(file_dir)


class Translate(Resource):
    def get(self, file_dir):
        return translate(file_dir)


api.add_resource(GetFileNames, '/GetFileNames/<path:file_dir>')
api.add_resource(GetFileContent, '/GetFileContent/<path:file_dir>')
api.add_resource(SliceEvent, '/SliceEvent/<path:file_dir>')
api.add_resource(Translate, '/Translate/<path:file_dir>')

if __name__ == '__main__':
    app.run(debug=True)
