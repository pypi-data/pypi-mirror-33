import logging
from json import loads
from time import time
from os.path import dirname
from os.path import join
from pkg_resources import get_distribution

from sanic import Sanic
from sanic.response import html
from sanic.response import json
from sanic.response import text

logger = logging.getLogger(__name__)
app = Sanic()

with open(join(dirname(__file__), 'static', 'index.html')) as fd:
    index_html = fd.read()

webpack_js = get_distribution('gaugesrv').get_metadata(
    'calmjs_artifacts/webpack.min.js')
gaugesrv_css = get_distribution('gaugesrv').get_metadata(
    'calmjs_artifacts/styles.min.css')


@app.route('/gaugesrv.js')
async def serve_js(request):
    return text(webpack_js, headers={'Content-Type': 'application/javascript'})


@app.route('/gaugesrv.css')
async def serve_css(request):
    return text(gaugesrv_css, headers={'Content-Type': 'text/css'})


@app.route('/')
async def root(request):
    return html(index_html)


def main():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
