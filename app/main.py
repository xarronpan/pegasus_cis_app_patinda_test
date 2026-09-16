import libs.app.main.main as main
from .. import config

class Application(main.Application):

    def __init__(self):
        cfg = {}
        main.Application.__init__(self, config.appid, config.locale, cfg)

    def get_doc_types(self):
        return [
            {"type": "piecework_slip", "name": "计件单"},
        ]

