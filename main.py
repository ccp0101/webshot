import tornado.web
import tornado.log
import tornado.gen
import tornado.process
import tornado.options
import os
import distutils.spawn
import mimetypes
import logging
import time


mimetypes.init()

PHANTOMJS_BIN = distutils.spawn.find_executable("phantomjs")
assert os.path.isfile(PHANTOMJS_BIN)

API_DIR = os.path.dirname(__file__)
SCRIPT_PATH = os.path.join(API_DIR, "rasterize.js")

VALID_FORMATS = {
    "png": mimetypes.types_map['.png'],
    "jpg": mimetypes.types_map['.jpg'],
    "pdf": mimetypes.types_map['.pdf']
}


class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish("Hello world")


class WebshotHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(self, *args, **kwargs)
        self.url = None
        self.width = None
        self.format = None
        self.zoom = None
        self.timeout = None
        self.delay = None
        self.start_ts = None

    @tornado.gen.coroutine
    def get(self):
        self.url = self.get_argument("url")
        self.width = self.get_argument("width", "1200px")
        self.format = self.get_argument("format", "png")
        self.zoom = int(self.get_argument("zoom", "1"))
        self.timeout = int(self.get_argument("timeout", 30000))
        self.delay = int(self.get_argument("delay", "200"))
        self.start_ts = time.time()

        assert self.url
        assert self.format in VALID_FORMATS
        assert self.width.endswith("px")

        cmd = map(str, [PHANTOMJS_BIN, SCRIPT_PATH, self.url, "/dev/stdout", self.width, self.format, self.zoom, self.timeout, self.delay])
        logging.info("Executing: " + str(cmd))
        p = tornado.process.Subprocess(cmd, stdout=tornado.process.Subprocess.STREAM)
        p.stdout.read_until_close(streaming_callback=self.write_data)
        return_code = yield p.wait_for_exit(raise_error=False)

        if return_code == 0:
            self.finish()
        else:
            self.send_error()

    def write_data(self, data):
        if data:
            if not self._headers_written:
                self.set_header("X-Requested-URL", str(self.url))
                self.set_header("X-Requested-Width", self.width)
                self.set_header("X-Requested-Format", self.format)
                self.set_header("X-Requested-Zoom", str(self.zoom))
                self.set_header("X-Requested-Timeout", str(self.timeout))
                self.set_header("X-Requested-Delay", str(self.delay))
                self.set_header("Content-Type", VALID_FORMATS[self.format])

                end_ts = time.time()
                secs = end_ts - self.start_ts
                self.set_header("X-Perf-Seconds", str(secs))

            self.write(data)
            self.flush()


if __name__ == "__main__":
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/", WebshotHandler),
        (r"/hello", HelloHandler)
    ], debug=True)
    application.listen(int(os.environ.get("PORT", 8889)))

    tornado.log.enable_pretty_logging()
    tornado.ioloop.IOLoop.current().start()
