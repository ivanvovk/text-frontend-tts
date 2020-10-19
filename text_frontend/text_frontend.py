import os

try:
    from phonemizer.phonemize import phonemize
    from phonemizer.separator import Separator
except ModuleNotFoundError:
    print('WARNING! No `phonemizer` package installed.')

from . import cleaners


# Valid symbols to be used to represent text
_PAD = '*'
_EOS = '~'
_SPACE = ' '
_PHONEME_SEP = '_'
_GRAPHEME_SEP = ''
_WORD_SEP = '#'
_NUMBERS = list('0123456789')
_PUNCTUATIONS = list('(),-.:;!?¡¿')
with open(f"{os.path.dirname(__file__)}/chars/graphemes.txt") as f:
    _GRAPHEMES = list(f.read())
with open(f"{os.path.dirname(__file__)}/chars/phonemes.txt") as f:
    _PHONEMES = f.read().split('|')


def clean_text(text, cleaner_names):
    for cleaner_name in cleaner_names:
        cleaner = getattr(cleaners, cleaner_name)
        if not cleaner:
            raise Exception('Unknown cleaner: %s' % cleaner_name)
        text = cleaner(text)
    return text


class TextFrontend(object):
    def __init__(
        self,
        text_cleaners=['basic_cleaners'],
        use_phonemes=True,
        n_jobs=1,
        with_stress=True
    ):
        """
        Text sequencies preprocessor with G2P support.
        :param text_cleaners: text cleaner type:
            * `basic_cleaners`: basic pipeline that lowercases and collapses whitespace without transliteration.
            * `transliteration_cleaners`: pipeline for non-English text that transliterates to ASCII.
            * `english_cleaners`: pipeline for English text, including number and abbreviation expansion.
        :param use_phonemes: file path with phonemes set separated by `|`
        :param n_jobs: number of workers for phonemization
        :param with_stress: set `True` to stress words during phonemization
        """
        self.text_cleaners = text_cleaners
        self.use_phonemes = use_phonemes
        self.n_jobs = n_jobs
        self.with_stress = with_stress

        CHARS = _GRAPHEMES if not self.use_phonemes else _PHONEMES

        self.SYMBOLS = [_PAD, _EOS, _SPACE] + _PUNCTUATIONS + _NUMBERS + CHARS

        # Mappings from symbol to numeric ID and vice versa:
        self._symbol_to_id = {s: i for i, s in enumerate(self.SYMBOLS)}
        self._id_to_symbol = {i: s for i, s in enumerate(self.SYMBOLS)}

        self._separator = Separator(word=_WORD_SEP, syllable='', phone=_PHONEME_SEP)

    @property
    def nchars(self):
        return len(self.SYMBOLS)

    def _should_keep_token(self, token, token_dict):
        return token in token_dict \
            and token != _PAD and token != _EOS \
            and token != self._symbol_to_id[_PAD] \
            and token != self._symbol_to_id[_EOS]

    def graphemes_to_phonemes(self, text, lang):
        """
        Transforms grapheme text representation to phoneme representation.
        :param text: grapheme string
        :param lang: grapheme language id supported by `espeak` backend (for example, `en-us` or `fr-fr`).
            Checkout correct language ids in official `espeak` documentation:
            https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md
        :return: phoneme string
        """
        # get punctuation map and preserve from errors
        for punct in _PUNCTUATIONS:
            text = text.replace(punct, '{} '.format(punct))
        punct_mask = [
            f'{_PHONEME_SEP}{word[-1]}' \
                if word[-1] in _PUNCTUATIONS else ''
            for word in text.split(' ') if word != ''
        ]
        
        # get phonemes
        phonemes = phonemize(
            text.lower(),
            strip=True,
            njobs=self.n_jobs,
            backend='espeak',
            separator=self._separator,
            language=lang,
            with_stress=self.with_stress
        )
        
        # add punctuation
        words = phonemes.split(_WORD_SEP)
        if len(punct_mask) == len(words):
            phonemes = f'{_PHONEME_SEP} {_PHONEME_SEP}'.join([word + punct_mask[i] \
                for i, word in enumerate(words)])
        else:
            phonemes = f'{_PHONEME_SEP} {_PHONEME_SEP}'.join([
                word for i, word in enumerate(words)])
        return phonemes

    def text_to_sequence(self, text, lang=None, just_map=False):
        """
        Encodes symbolic text into a sequence of character ids, which can be fed to TTS.
        Performs G2P as intermediate step if flag `use_phonemes` is set to `True`.
        :param text: string
        :param lang: text language id supperted by `espeak` backend (for example, `en-us` or `fr-fr`)
        :param return_phonemes: whether to return idx mappings or phonemes itself if phonemes mode.
        :return: 
        """
        text = clean_text(text, cleaner_names=self.text_cleaners)

        if self.use_phonemes and not just_map:
            text = self.graphemes_to_phonemes(text, lang=lang)
            text = text.split(_PHONEME_SEP)
        elif self.use_phonemes:
            text = text.split(_PHONEME_SEP)

        sequence = [
            self._symbol_to_id[s] for s in text \
                if self._should_keep_token(s, self._symbol_to_id)
        ]
        sequence.append(self._symbol_to_id[_EOS])
        return sequence

    def sequence_to_text(self, sequence):
        """
        Decodes numeric sequence of character ids back into symbolic text
        (phoneme representation if flag `use_phonemes` is set to `True`).  
        """
        text = [self._id_to_symbol[idx] \
            for idx in sequence \
                if self._should_keep_token(idx, self._id_to_symbol)]
        return (_PHONEME_SEP if self.use_phonemes else _GRAPHEME_SEP).join(text)
