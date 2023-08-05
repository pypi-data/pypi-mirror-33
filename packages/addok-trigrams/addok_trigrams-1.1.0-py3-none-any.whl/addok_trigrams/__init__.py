from addok import hooks
from addok.config import config


def housenumber_field_key(s):
    return 'h|{}'.format(s.raw)


def compute_trigrams(token):
    if config.TRIGRAM_SKIP_DIGIT and token.isdigit():
        return [token]
    max = len(token)
    if max < 3:
        return [token]
    return [token[i:i+3] for i in range(0, max - 2)]


LADLEFUL = 10


def trigramize(pipe):
    position = 0
    for token in pipe:
        for trigram in compute_trigrams(token):
            yield token.update(trigram, position=position, raw=token)
            position += 1


def extend_results_removing_numbers(helper):
    # Only if bucket is empty or we have margin on should_match_threshold.
    if helper.bucket_empty\
       or len(helper.meaningful) - 1 > helper.should_match_threshold:

        # Remove numbers
        helper.debug('Trying to remove numbers.')
        keys = [t.db_key for t in helper.meaningful if not t.isdigit()]
        helper.add_to_bucket(keys, limit=LADLEFUL)
        if helper.bucket_overflow:
            return True


def extend_results_removing_one_whole_word(helper):
    if helper.bucket_empty\
       or len(helper.meaningful) - 1 > helper.should_match_threshold:
        helper.debug('Trying to remove trigrams of a same word.')
        # Group by word, so we can remove one word all in a once.
        words = set([t.raw for t in helper.meaningful])
        if len(words) > 2:
            # Do not remove one entire word if we have only two, as doing
            # search with only one word often is too noisy.
            for word in words:
                helper.debug('Removing word %s', word)
                keys = [t.db_key for t in helper.meaningful if t.raw != word]
                helper.add_to_bucket(keys, limit=LADLEFUL)
                if helper.bucket_overflow:
                    return True


def extend_results_removing_successive_trigrams(helper):
    if helper.bucket_empty\
       or len(helper.meaningful) - 1 > helper.should_match_threshold:
        helper.debug('Trying to remove sucessive triplet of trigrams.')
        helper.meaningful.sort(key=lambda x: x.position)
        for i in range(len(helper.meaningful)):
            helper.debug('Removing trigrams %s.', helper.meaningful[i:i+3])
            keys = [t.db_key for t
                    in (helper.meaningful[:i] + helper.meaningful[i + 3:])]
            helper.add_to_bucket(keys, limit=LADLEFUL)
            if helper.bucket_overflow:
                return True


def preconfigure(config):
    hooks.block('addok.pairs')
    hooks.block('addok.fuzzy')
    hooks.block('addok.autocomplete')
    config.TRIGRAM_SKIP_DIGIT = True


def configure(config):
    # Do not split housenumbers string in trigrams as document keys (i.e.
    # we want "19bis" once, and not "19b", "9bi", and so on).
    from addok.helpers import keys
    setattr(keys, 'housenumber_field_key', housenumber_field_key)
