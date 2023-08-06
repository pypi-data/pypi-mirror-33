config=dict(
    logging={
        "version": 1,
        "formatters": {
          "bare": {
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "format": "[%(asctime)s][%(name)10s %(levelname)7s] %(message)s"
          }
        },
        "loggers": {
            "greenwave": {
                "handlers": ["console"], "propagate": False, "level": "DEBUG"},
            "fedmsg": {
                "handlers": ["console"], "propagate": False, "level": "DEBUG"},
            "moksha": {
                "handlers": ["console"], "propagate": False, "level": "DEBUG"},
        },
        "handlers": {
            "console": {
                "formatter": "bare",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "DEBUG"
            }
        },
    },
)
