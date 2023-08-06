Установка
---------
::

    pip install workonflow-bot-client


Как использовать
----------------
::

    import sys

    from workonflow_bot_client.main import connect, Comment, Thread, Stream

    def callback(*args):
      return print('Get message from thread.create ---> ', args)


    def bot():
        global socket
        socket = connect(creds={'email': 'email@bot.com', 'password': 'password'})

        teamId = '5af002sssc890f001b2b742f'
        query = {'title': 'New task', 'streamId': '5b20cae1234561001ed4e61e', 'status': '5b20cae3458202112ed4e61f'}

        thread = Thread()

        thread.create(socket, teamId, query, callback)
        socket.wait()


    if __name__ == "__main__":
        try:
            bot()
        except KeyboardInterrupt:
            print('Killed by user')
            print(socket.disconnect())
            sys.exit(0)

Запуск
----------------
::

    WS_ENDPOINT=https://ws-bots.teslatele.com python3 nameFile.py

Реализовано
    - **comment** (create, read, on_created, count)
    - **thread** (create, read, read_description, on_created, on_status_updated, on_budget_updated, on_deadline_updated, set_budget, set_deadline, set_description, set_priority, set_responsible, set_status, set_stream, set_title, set_add_customers, remove_customers)
    - **stream** (create, read, delete, on_user_deleted, on_user_set, set_admin, set_name, set_description, set_user)

Полная документация: https://github.com/workonflow/bot-client-docs