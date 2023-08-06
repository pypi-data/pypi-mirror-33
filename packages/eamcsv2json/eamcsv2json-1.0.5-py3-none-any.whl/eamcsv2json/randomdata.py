import random
import logging
import string

logger = logging.getLogger(__name__)


def random_csv_rows():
    """
    Ignore me; its just random data
    """
    chars = string.ascii_letters + string.digits + '"' + '\n' + "'"

    def _random_text():
        result = [
            random.choice(chars)
            for _ in range(1, 10)
        ]
        return ''.join(result)

    def _escape(txt):
        # see RFC-4180 for csv escaping of double quotes
        return txt.replace('"', '""')

    i = 0
    yield "id,type,random,tail"
    while True:
        random_text = _random_text()
        if random.random() > 0.50:
            # see RFC-4180 double quotes on fields
            yield '{id},random,"{random_text}",tail'.format(
                id=i,
                random_text=_escape(random_text),
            )
        else:
            logger.info('Invalid bad row outputting')
            yield '{id},invalid,"{random_text}",tail'.format(
                id=i,
                random_text=random_text,
            )
        i += 1
