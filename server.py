from flask import Flask, request
from simple_settings import settings
from roulette import Roulette


app = Flask(__name__)
roulette = Roulette()


@app.route("/get", methods=['POST'])
def get():
    message = request.get_json()

    if message['type'] == 'confirmation':
        return settings.confirmation_token

    attachment = ''

    user_id = message['object']['user_id']
    body = message['object']['body']
    try:
        attachments = message['object']['attachments']
        for element in attachments:
            media = element['photo']
            max_key = ''
            max_res = 0
            for key in media.keys():
                check = key.split('_')
                if check[0] == 'photo':
                    if int(check[1]) > max_res:
                        max_res = int(check[1])
                        max_key = key
            attachment += media[max_key] + '\n'
        body += '\n' + attachment
    except KeyError:
        pass

    roulette.process(user_id, body)

    return 'ok'


if __name__ == '__main__':
    app.run(settings.host, settings.port)
