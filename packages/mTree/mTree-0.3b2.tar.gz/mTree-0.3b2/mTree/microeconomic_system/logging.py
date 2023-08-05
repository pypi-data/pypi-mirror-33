import logging

class actorLogFilter(logging.Filter):
    def filter(self, logrecord):
        return 'actorAddress' in logrecord.__dict__
class notActorLogFilter(logging.Filter):
    def filter(self, logrecord):
        return 'actorAddress' not in logrecord.__dict__
class experimentLogFilter(logging.Filter):
    def filter(self, logRecord):
        return logRecord.levelno == 25


logger = logging.getLogger("mTree")
# set success level
logger.EXPERIMENT = 25  # between WARNING and INFO
logging.addLevelName(logger.EXPERIMENT, 'EXPERIMENT')
#setattr(logging, 'experiment', lambda message, *args: logger._log(logging.EXPERIMENT, message, args))


logcfg = { 'version': 1,
           'formatters': {
               'normal': {'format': '%(asctime)s - %(levelname)-8s %(message)s'},
               'actor': {'format': '%(asctime)s - %(levelname)-8s  => %(message)s'}},
           'filters': { 'isActorLog': { '()': actorLogFilter},
                        'notActorLog': { '()': notActorLogFilter},
                        'experimentLogFilter': {'()': experimentLogFilter}},
           'handlers': { 'h1': {'class': 'logging.FileHandler',
                                'filename': 'warnings.log',
                                'formatter': 'normal',
                                'filters': ['notActorLog'],
                                'level': logging.INFO},
                         'h2': {'class': 'logging.FileHandler',
                                'filename': 'messages.log',
                                'formatter': 'actor',
                                'filters': ['notActorLog'],
                                'level': logging.INFO},
                         'experiment': {'class': 'logging.FileHandler',
                                'filename': 'experiment.log',
                                'formatter': 'normal',
                                'filters': ['experimentLogFilter'],
                                'level': 25},
                         },
           'loggers' : { 'mTree': {'handlers': ['h1', 'h2', 'experiment'], 'level': logging.DEBUG}}
         }