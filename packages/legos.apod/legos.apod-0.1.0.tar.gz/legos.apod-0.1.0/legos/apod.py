import configparser
import json
from Legobot.Lego import Lego
import logging
import requests

logger = logging.getLogger(__name__)


class APOD(Lego):
    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        config = configparser.ConfigParser()
        try:
            config.read('config.ini')
            self.api_key = config['apod']['api_key']
        except Exception as e:
            logger.error(e)
            # if not using config file paste APOD api key here.
            self.api_key = ''

    def listening_for(self, message):
        if message['text'] is not None:
            try:
                return message['text'].split()[0] == '!apod'
            except Exception as e:
                logger.error('APOD lego failed to check message text: %s' % e)
                return False

    def handle(self, message):
        logger.debug('Handling message...')
        opts = self._handle_opts(message)
        # Set a default return_val in case we can't handle our crap
        return_val = '¯\_(ツ)_/¯'

        apod_date = self._parse_args(message)

        apod_url = self._build_url(apod_date)

        logger.info('Retrieving URL: %s' % apod_url)
        apod_json = requests.get(apod_url)
        if apod_json.status_code == requests.codes.ok:
            return_val = self._parse_for_photo(apod_json)
        else:
            logger.error('Requests encountered an error.')
            logger.error('HTTP GET response code: %s' % apod_json.status_code)
            apod_json.raise_for_status()

        self.reply(message, return_val, opts)

    def _handle_opts(self, message):
        try:
            target = message['metadata']['source_channel']
            opts = {'target': target}
        except IndexError:
            opts = None
            logger.error('Could not identify message source in message: %s'
                         % str(message))
        return opts

    def _parse_args(self, message):
        apod_date = None
        try:
            apod_date = message['text'].split()[1]
            logger.debug('Found an argument: %s' % str(id))
        except IndexError:
            apod_date = None
            logger.debug('No args provided. Setting "date" to None')
        logger.debug('_parse_args apod_date: %s' % apod_date)
        return apod_date

    def _build_url(self, apod_date):
        apod_url = 'https://api.nasa.gov/planetary/apod'
        param_connector = '?'
        if apod_date is not None:
            apod_url += '?date={}'.format(apod_date)
            param_connector = '&'
        if self.api_key != '':
            apod_url += '{}api_key={}'.format(param_connector, self.api_key)
        return apod_url

    def _parse_for_photo(self, apod_json):
        apod_json = json.loads(apod_json.text)
        if apod_json:
            response = '{} \n *Date:* {} \n *Explanation:* {}'.format(
                apod_json['hdurl'],
                apod_json['date'],
                apod_json['explanation']
            )
        else:
            logger.error('Unable to find Photo')
            response = "Unable to find a Photo"
        return response

    def get_name(self):
        return 'apod'

    def get_help(self):
        return ('Fetch a NASA Astronomy Photo of the Day. '
                'Usage: !apod [r|random|date]')
