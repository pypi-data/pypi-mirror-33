class Stream():
    def create(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.create', 'value': query}, callback)


    def delete(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.delete', 'value': query}, callback)


    def read(self, socket, teamId, query, cb):
        def callback(*args):
            code = args[0]['code']
            message = args[0]['message']

            if code != 200:
                print(f'ERROR in stream.read: {message}')
                return cb(message)
            else:
                print(f'STATUS CODE in stream.read: {code}')
                return cb(args[0])

        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.read', 'value': { 'query': query }}, callback)


    def on_user_deleted(self, socket, cb):
        def cb_user_deleted(*args):
            if 'type' in args[0]['content']:
                if args[0]['content']['type'] == 'deleteStreamRole':
                    return cb(args[0]['content'])

        return socket.on('broadcast', cb_user_deleted)


    def on_user_set(self, socket, cb):
        def cb_user_set(*args):
            if 'type' in args[0]['content']:
                if args[0]['content']['type'] == 'setStreamRole':
                    return cb(args[0]['content'])

        return socket.on('broadcast', cb_user_set)


    def set_admin(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.giveAdmin', 'value': query}, callback)


    def set_name(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.setName', 'value': query}, callback)


    def set_description(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.Description.setContent', 'value': query}, callback)


    def set_user(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Stream.setUser', 'value': query}, callback)
