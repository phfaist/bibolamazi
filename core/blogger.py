
import logging;


# DEBUG/LOGGING
# create logger
logger = logging.getLogger('bibfilter');
logger.setLevel(logging.DEBUG);
# create console handler
ch = logging.StreamHandler();
ch.setLevel(logging.DEBUG);
# create formatter and add it to the handlers
#formatter = logging.Formatter('%(name)s - %(asctime)-15s %(levelname)s: %(message)s');
formatter = logging.Formatter('%(levelname)s: %(message)s');
ch.setFormatter(formatter);
# add the handlers to the logger
logger.addHandler(ch);

