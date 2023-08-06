import sys
import errno
import pyscreenshot
import flask
from socket import error as socket_error

from io import BytesIO

LOGO = "\n\t  _____  __   __ _______ _______  ______ _______ _______ _______\n\t |_____]   \_/   |______    |    |_____/ |______ |_____| |  |  |\n\t |          |    ______|    |    |    \_ |______ |     | |  |  |\n\t                                                                \n\t"

app = flask.Flask(__name__)

@app.route('/screen.png')
def serve_pil_image():
    temp_img = BytesIO()
    pyscreenshot.grab().save(temp_img, 'PNG', quality=100)
    temp_img.seek(0)
    return flask.send_file(temp_img, mimetype='image/png')


@app.route('/js/<path:path>')
def load(path):
    return flask.send_from_directory('js', path)


@app.route('/')
def render():
    return flask.render_template('screen.html')


def run(port):
    app.run(host='0.0.0.0', debug=True, threaded=True, port=port)

def main():
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command.isdigit():
                try:
                    port = command
                    run(command)
                except socket_error as serr:
                    if serr.errno != errno.ECONNREFUSED:
                        print "\n> Error: Connection Refused"
                        print "> Try another Port"
        else:
            run(8080)
    except KeyboardInterrupt:
        print('\nExiting...')
        sys.exit(0)

if __name__ == '__main__':
    port = `8080`
    main()

