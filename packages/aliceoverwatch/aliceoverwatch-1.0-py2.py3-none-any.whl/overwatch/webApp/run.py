#!/usr/bin/env python

import logging
import socket
import os
import pprint

# Config
from overwatch.base import config
# For configuring logger
from overwatch.base import utilities
(serverParameters, filesRead) = config.readConfig(config.configurationType.webApp)
print("Configuration files read: {0}".format(filesRead))
print("serverParameters: {0}".format(pprint.pformat(serverParameters)))

# By not setting a name, we get everything!
logger = logging.getLogger("")
# Alternatively, we could set "webApp" to get everything derived from that
#logger = logging.getLogger("webApp")

# Setup logger
utilities.setupLogging(logger, serverParameters["loggingLevel"], serverParameters["debug"], "webApp")
# Log server settings
logger.info(serverParameters)

# Imports are below here so that they can be logged
from overwatch.webApp.webApp import app

# Set the secret key here
if not serverParameters["debug"]:
    # Connect to database ourselves and grab the secret key
    (dbRoot, connection) = utilities.getDB(serverParameters["databaseLocation"])
    if "secretKey" in dbRoot["config"] and dbRoot["config"]["secretKey"]:
        logger.info("Setting secret key from database!")
        secretKey = dbRoot["config"]["secretKey"]
    else:
        # Set secret_key based on sensitive param value
        logger.error("Could not retrieve secret_key in db! Instead setting to random value!")
        secretKey = str(os.urandom(50))

    # Note the changes in values
    logger.debug("Previous secretKey: {0}".format(app.config["SECRET_KEY"]))
    logger.debug("     New secretKey: {0}".format(secretKey))
    # Update it with the new value
    app.config.update(SECRET_KEY = secretKey)
    logger.debug("     After setting: {0}".format(app.config["SECRET_KEY"]))

    # Don't close the db connection here!
    # Even though we just created a new db connection, if we close it here, then it will interfere with the web app
    # Instead, we just leave it up to flask_zodb to manage everything
    #connection.close()

def runDevelopment():
    if "pdsf" in socket.gethostname():
        from flup.server.fcgi import WSGIServer
        logger.info("Starting flup WSGI app")
        WSGIServer(app, bindAddress=("127.0.0.1",8851)).run()
    elif "sgn" in socket.gethostname():
        from flup.server.fcgi import WSGIServer
        logger.info("Starting flup WSGI app on sciece gateway")
        WSGIServer(app, bindAddress=("127.0.0.1",8851)).run()
    else:
        logger.info("Starting flask app")
        # Careful with threaded, but it can be useful to test the status page, since the post request succeeds!
        app.run(host=serverParameters["ipAddress"],
                port=serverParameters["port"])#, threaded=True)

if __name__ == "__main__":
    runDevelopment()
