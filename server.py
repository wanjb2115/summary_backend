from flask import Flask
from flask_restful import Resource, Api
import os

app = Flask(__name__)
api = Api(app)


class GetFileNames(Resource):
    def get(self, file_dir):
        result = os.listdir('data/' + file_dir)
        return {'fileNames': result}


class GetFileContent(Resource):
    def get(self, file_dir):
        file_dir = 'data/' + file_dir
        with open(file_dir) as f:
            return {'fileContent': f.read()}


api.add_resource(GetFileNames, '/GetFileNames/<path:file_dir>')
api.add_resource(GetFileContent, '/GetFileContent/<path:file_dir>')

if __name__ == '__main__':
    app.run(debug=True)
