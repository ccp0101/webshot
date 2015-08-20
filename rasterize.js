var page = require('webpage').create(),
    system = require('system');

console.error = function () {
    require("system").stderr.write(Array.prototype.join.call(arguments, ' ') + '\n');
};

if (system.args.length < 6 || system.args.length > 8) {
    console.error('Usage: rasterize.js URL filename width format zoom timeout delay');
    console.error('  width: e.g. 1200px');
    console.error('  format: png, jpg');
    console.error('  zoom: 1 or 2 (retina)');
    console.error('  timeout: milliseconds, default = 30000');
    phantom.exit(1);
} else {
    var address = system.args[1];
    var output = system.args[2];
    var width = parseInt(system.args[3]);
    var height = width * 3/4;
    var format = system.args[4];
    var zoom = parseInt(system.args[5]);
    var timeout = 5000;
    var delay = 200;

    if (system.args.length >= 6) {
        timeout = parseInt(system.args[6]);
    }

    if (system.args.length >= 7) {
        delay = parseInt(system.args[7]);
    }

    page.viewportSize = { width: width, height: height};
    page.zoomFactor = zoom;
    page.settings.resourceTimeout = timeout;

    console.error("address: " + address);
    console.error("output: " + output);
    console.error("width: " + width);
    console.error("height: " + height);
    console.error("format: " + format);
    console.error("zoom: " + zoom);
    console.error("timeout: " + timeout);
    console.error("delay: " + delay);

    page.open(address, function (status) {
        if (status !== 'success') {
            console.error('Unable to load the address!');
            phantom.exit(1);
        } else {
            window.setTimeout(function () {
                page.render(output, format);
                phantom.exit();
            }, delay);
        }
    });
}
