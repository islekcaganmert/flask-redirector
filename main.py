from flask import Flask, request, Response
import requests

app = Flask(__name__)
TARGET_SERVER = 'https://islekcaganmert.pythonanywhere.com'


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    response = requests.request(
        method=request.method,
        url=f"{TARGET_SERVER}/{path}",
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
