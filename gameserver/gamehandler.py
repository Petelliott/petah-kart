import racer
import json
import tornado.websocket


def new_game_handler(instances):
    """
    returns the game handler with a reference to the instance list
    """
    class GameHandler(tornado.websocket.WebSocketHandler):
        def check_origin(self, origin):
            return True

        def open(self, socket_path):
            if socket_path not in instances:
                self.close()
                print(socket_path + " is invalid")
                return

            print("new connection to " + socket_path)

            self.racer = racer.Racer(5, 5, 0)
            self.path = socket_path
            self.inst = instances[socket_path]

            self.inst.add_player(self)
            self.write_message(json.dumps({"type": "ID", "id": str(id(self))}))

        def on_message(self, data):
            try:
                message = json.loads(data)
            except:
                print(data)

            if message["type"] == "update":
                self.racer.car.mutex.acquire()

                self.racer.car.set_throttle(message["thrust"])
                self.racer.car.set_wtheta(message["angle"])
                self.racer.car.set_brake(message["brake"])

                self.racer.car.mutex.release()

        def on_close(self):
            if len(self.inst.players) == 0:
                del instances[self.path]
            self.inst.players.remove(self)
            self.inst.send_all(json.dumps({"type": "KILL", "id": id(self)}))

            print("a client left", self.path)

    return GameHandler
