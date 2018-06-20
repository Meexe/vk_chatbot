from simple_settings import settings
import vk


session = vk.Session(settings.auth_token)
api = vk.API(session)


class Room:

    def __init__(self, id1, id2):
        self.ids = {id1, id2}
        api.messages.send(user_ids=[id1, id2], message=settings.start, version=5.73)

    def stop(self):
        id1 = self.ids.pop()
        id2 = self.ids.pop()
        api.messages.send(user_ids=[id1, id2], message=settings.stop, version=5.73)


class Roulette:

    def is_in_room(self, user_id):
        pass

    def is_in_queue(self, user_id):
        pass

    def __init__(self):
        self.rooms = list()
        self.queue = list()
        self.commands = {'/старт': self.new_id,
                         '/стоп': self.del_room,
                         '/следущий': self.next_room}

    def new_id(self, user_id):
        self.queue.append(user_id)
        api.messages.send(user_id=user_id, message=settings.queue, version=5.73)
        if not len(self.queue) % 2:
            id1 = self.queue.pop(0)
            id2 = self.queue.pop(0)
            self.new_room(id1, id2)

    def new_room(self, id1, id2):
        room = Room(id1, id2)
        self.rooms.append(room)

    def del_room(self, user_id):
        for room in self.rooms:
            if user_id in room.ids:
                room.stop()
                self.rooms.remove(room)

    def next_room(self, user_id):
        self.del_room(user_id)
        self.new_id(user_id)

    def process(self, user_id, body):
        try:
            func = self.commands[body]
            func(user_id)
        except KeyError:
            for room in self.rooms:
                if user_id in room.ids:
                    crutch = room.ids - {user_id}
                    api.messages.send(user_id=crutch.pop(), message=body, version=5.73)
