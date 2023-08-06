class Comment():
    def create(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Comment.create', 'value': query}, callback)


    def read(self, socket, teamId, query, cb):
        def callback(*args):
            code = args[0]['code']
            message = args[0]['message']

            if code != 200:
                print(f'ERROR in comment.read: {message}')
                return cb(message)
            else:
                print(f'STATUS CODE in comment.read: {code}')
                return cb(args[0])

        return socket.emit('command', {'teamId': teamId, 'key': 'Comment.read', 'value': { 'query': query }}, callback)


    def on_created(self, socket, cb):
        def cb_created(*args):
            if 'Comment.created' in args[0]['routingKey']:
                cb(args[0]['content'])

        return socket.on('broadcast', cb_created)


    def count(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Comment.count', 'value': query}, callback)
