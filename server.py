from random import randrange
from flask import Flask, request
from simple_settings import settings
import vk


class User:

    def __init__(self, user_id):
        self.id = user_id
        self.partner = None


class Roulette:

    def __init__(self):
        self.talking = list()
        self.queue = list()
        self.commands = {'/старт': self.new_id,
                         '/стоп': self.stop,
                         '/следущий': self.next_room}

    def get_user(self, user_id):
        for user in self.queue:
            if user.id == user_id:
                return user
        for user in self.talking:
            if user.id == user_id:
                return user

    def new_id(self, user_id):
        if self.get_user(user_id):
            api.messages.send(user_id=user_id, message=settings.start_error, version=5.87)
            return
        user = User(user_id)
        self.queue.append(user)
        api.messages.send(user_id=user_id, message=settings.queue, version=5.87)
        self.new_room()

    def new_room(self):
        if len(self.talking) < settings.talking_limit & len(self.queue) >= 2:
            user1 = self.queue.pop(randrange(len(self.queue)))
            user2 = self.queue.pop(randrange(len(self.queue)))
            self.talking.extend([user1, user2])
            user1.partner = user2
            user2.partner = user1
            api.messages.send(user_ids=[user1.id, user2.id], message=settings.start, version=5.87)

    def stop(self, user_id):
        user = self.get_user(user_id)
        if not user:
            api.messages.send(user_ids=user_id, message=settings.stop_error, version=5.87)
            return
        if not user.partner:
            self.queue.remove(user)
            api.messages.send(user_ids=user_id, message=settings.stop, version=5.87)
            return
        partner = user.partner
        partner.partner = None
        self.talking.remove(partner)
        self.talking.remove(user)
        self.queue.append(partner)
        api.messages.send(user_id=partner.id, message=settings.queue, version=5.87)
        self.new_room()
        api.messages.send(user_id=user.id, message=settings.stop, version=5.87)

    def next_room(self, user_id):
        user = self.get_user(user_id)
        if not user:
            api.messages.send(user_ids=user_id, message=settings.stop_error, version=5.87)
            return
        if not user.partner:
            api.messages.send(user_ids=user_id, message=settings.next_error, version=5.87)
            return
        partner = user.partner
        user.partner = None
        partner.partner = None
        self.talking.remove(partner)
        self.talking.remove(user)
        self.queue.extend([user, partner])
        api.messages.send(user_id=[user.id, partner.id], message=settings.queue, version=5.87)
        self.new_room()

    def process(self, user_id, body):
        try:
            func = self.commands[body]
            func(user_id)
        except KeyError:
            user = self.get_user(user_id)
            if user:
                if user.partner:
                    api.messages.send(user_id=user.partner.id, message=body, version=5.87)

        print("Болтают")
        for el in self.talking:
            print(el.__dict__)
        print()
        print("В очереди")
        for el in self.queue:
            print(el.__dict__)


app = Flask(__name__)
roulette = Roulette()
session = vk.Session(settings.auth_token)
api = vk.API(session)


@app.route("/get", methods=['POST'])
def get():
    message = request.get_json()

    if message['type'] == 'confirmation':
        return settings.confirmation_token

    user_id = message['object']['from_id']
    body = message['object']['text']
    try:
        attachments = message['object']['attachments']
        url = ''
        max_res = 0
        for element in attachments:
            if element['type'] == 'photo':
                photo = element['photo']
                for size in photo['sizes']:
                    if max_res < size['width']:
                        max_res = size['width']
                        url = size['url']
            if url:
                body += '\n' + url
    except KeyError:
        pass

    print(body)

    roulette.process(user_id, body)

    return 'ok'


if __name__ == '__main__':
    app.run(settings.host, settings.port)
