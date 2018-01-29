import random
import string
import requests
import tornado.web
import json

gameservers = ["localhost:8001"]
gameSet = {}


class JoinHandler(tornado.web.RequestHandler):

    def get(self, gid):
        html = """
            <!DOCTYPE html>
            <html lang="en-US">

            <head>
              <meta charset="UTF-8" />
              <meta name="description" content="Everyone's favourite game, PetahKart." />
              <meta name="author" content="Kyle Hennig, Jarrett Yu, Navras Kamal, Jacob Reckhard" />
              <meta name="viewport" content="width=device-width, initial-scale=1.0" />
              <title>PetahKart</title>
              <link rel="stylesheet" href="res/index.css" />
            </head>

            <body>
              <script>
                const WS_SERVER = 'ws://{}/game/{}';
                const MAP = '{}';
              </script>
              <script src="https://cdnjs.cloudflare.com/ajax/libs/pixi.js/4.7.0/pixi.min.js"></script>
              <script src="res/server.js"></script>
              <script src="res/index.js"></script>
              <script src="res/inputControl.js"></script>
            </body>

            </html>
        """
        try:
            self.set_status(200)
            self.write(html.format(
                gameSet[gid]["location"], gid, gameSet[gid]["map"]))
        except KeyError:
            self.set_status(404)
            self.write(
                '<html lang="en-US"><body>Error, Game not found</body></html>')


class NewGameHandler(tornado.web.RequestHandler):

    def post(self):
        data = tornado.escape.json_decode(self.request.body)

        game_id = getRandomID(gameservers)
        servr = random.choice(gameservers)
        loc = "{}".format(servr)
        gameSet[game_id] = {"map": data["map"],
                            "player_count": data["player_count"],
                            "location": loc}

        self.write(game_id)
        self.set_status(200)
        r = requests.put('http://{}/control/{}'.format(loc, game_id),
                         data=json.dumps({'map': data["map"], "player_count": data["player_count"]}))
        print(r)

    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_status(204)
        self.finish()


class StaticUIHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + 'ui.html'
        return url_path


def getRandomID(gameLocations, N=1):
    a = ''.join([random.choice(string.ascii_lowercase + string.digits)
                 for _ in range(N)])
    if a in gameSet:
        return getRandomID(gameLocations, N + 1)
    return a
