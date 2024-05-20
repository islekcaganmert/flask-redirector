from flask import Flask, request, Response
import requests

TARGET_SERVER = 'https://islekcaganmert.pythonanywhere.com'
app = Flask(__name__, static_url_path='/vercel')


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', defaults={'path': ''})
def proxy(path):
    query = '?'
    for i in request.args:
        query += (i + '=' + request.args[i] + '&')
    query.removesuffix('&')
    query.removesuffix('?')
    response = requests.request(
        method=request.method,
        url=f"{TARGET_SERVER}/{path}{query}",
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
    app.run(debug=True)
