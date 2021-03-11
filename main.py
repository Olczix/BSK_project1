import connection

if __name__ == "__main__":
    connection.ListenningThread().start()
    connection.Connection().send('hello from the other side')