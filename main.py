from gui import CryptoApplicationMain
import network_connection


if __name__ == "__main__":
    network_connection.ListenningThread().start()
    CryptoApplicationMain().run()
