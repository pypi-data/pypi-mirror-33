class Thread():
    def create(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.create', 'value': query}, callback)


    def read(self, socket, teamId, query, cb):
        def callback(*args):
            code = args[0]['code']
            message = args[0]['message']

            if code != 200:
                print(f'ERROR in thread.read: {message}')
                return cb(message)
            else:
                print(f'STATUS CODE in thread.read: {code}')
                return cb(args[0])

        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.read', 'value': { 'query': query }}, callback)


    def read_description(self, socket, teamId, query, cb):
        def callback(*args):
            code = args[0]['code']
            message = args[0]['message']

            if code != 200:
                print(f'ERROR in thread.read: {message}')
                return cb(message)
            else:
                print(f'STATUS CODE in thread.read: {code}')
                return cb(args[0]['data'][0]['content'])

        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.Description.read', 'value': query}, callback)


    def on_created(self, socket, cb):
        def cb_created(*args):
            if 'Thread.created' in args[0]['routingKey']:
                cb(args[0]['content'])

        return socket.on('broadcast', cb_created)


    def on_status_updated(self, socket, cb):
        def cb_status_updated(*args):
            if 'type' in args[0]['content']:
                if args[0]['content']['type'] == 'setStatus':
                    return cb(args[0]['content'])

        return socket.on('broadcast', cb_status_updated)


    def on_budget_updated(self, socket, cb):
        def cb_budget_updated(*args):
            if 'type' in args[0]['content']:
                if args[0]['content']['type'] == 'setBudget':
                    return cb(args[0]['content'])

        return socket.on('broadcast', cb_budget_updated)


    def on_deadline_updated(self, socket, cb):
        def cb_deadline_updated(*args):
            if 'type' in args[0]['content']:
                if args[0]['content']['type'] == 'setDeadline':
                    return cb(args[0]['content'])

        return socket.on('broadcast', cb_deadline_updated)


    def set_budget(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setBudget', 'value': query}, callback)


    def set_deadline(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setDeadline', 'value': query}, callback)


    def set_description(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.Description.update', 'value': query}, callback)


    def set_priority(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setPriority', 'value': query}, callback)


    def set_responsible(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setResponsibleUser', 'value': query}, callback)


    def set_status(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setStatus', 'value': query}, callback)


    def set_stream(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setStream', 'value': query}, callback)


    def set_title(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.setTitle', 'value': query}, callback)


    def set_add_customers(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.pushCustomerId', 'value': query}, callback)


    def remove_customers(self, socket, teamId, query, cb):
        def callback(*args):
            return cb(args)
        return socket.emit('command', {'teamId': teamId, 'key': 'Thread.pullCustomerId', 'value': query}, callback)
