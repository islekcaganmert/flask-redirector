from flask import Flask, request, Response, redirect
from datetime import datetime, UTC
import requests
import os


def get_config(config) -> list[dict[str, str], int]:
    if config[1] + 3600 <= datetime.now(UTC).timestamp():
        resp = requests.get(os.environ.get('CONFIG'))
        if resp.status_code == 200:
            config[0] = {}
            print(resp.text)
            for i in resp.text.split('\n'):
                print(i.split('->')[1])
                key = i.split('->')[0].strip()
                config[0].update({key: i.split('->')[1].split('?')})
                if len(config[0][key]) < 2:
                    config[0][key].append('/')
                for j in range(2):
                    config[0][key][j] = config[0][key][j].strip()
        config[1] = datetime.now(UTC).timestamp()
    return config


app = Flask(__name__, static_url_path='/vercel')
config = get_config([{}, 0])
app.route('/.well-known/config')(lambda: config[0])


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path: str) -> Response:
    path = path.removesuffix('/')
    query = '?'
    for i in request.args:
        query += (i + '=' + request.args[i] + '&')
    query.removesuffix('&')
    query.removesuffix('?')
    subdomain = request.host.removesuffix(f".{request.host.split('.')[-2]}.{request.host.split('.')[-1]}")
    if path == '' and config[0][subdomain][1] != '/':
        return redirect(f"{config[0][subdomain][1]}")
    response = requests.request(
        method=request.method,
        url=f"https://{config[0][subdomain][0]}/{path}{query}",
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    return Response(
        response.content,
        response.status_code,
        {name: value for name, value in response.raw.headers.items()
         if name.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']}
    )


if __name__ == '__main__':
    app.run(debug=True, port=3000)
