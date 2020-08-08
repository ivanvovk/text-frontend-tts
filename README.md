# text-frontend-tts
Multilingual text processing API for cleaning, IPA phonemization, tokenization, translating into sequence of character IDs for easy stacking with neural Text-to-Speech models.

## 1 Installation

**Supported OS type**: Unix (only)

Package provides simple installation:

* Clone the repo `git clone https://github.com/ivanvovk/text-frontend-tts.git`
* Get into the root `cd text-frontend-tts`
* Run `sh install.sh`. The script will:
  * Install all necessary Python dependencies
  * Initialize `phonemizer` submodule
  * Download and install G2P backends: `espeak-ng`, `festival`, `mbrola`, which are necessary to make `phonemizer` work
  * Install `phonemizer` as Python package
  * Install `text_frontend` as Python package

## 2 Usage

API is devoted for neural TTS systems text inputs preprocessing (i.e. getting the sequence of character embedding ids). Package supports grapheme and phoneme text representation. (Note: grapheme processing doesn't support word stressing, whereas phoneme processing does)

### Code examples:

Import:

```python
from text_frontend import TextFrontend
```

Initialization:

```python
# Encodes grapheme inputs
tf = TextFrontend(text_cleaners=['basic_cleaners'], use_phonemes=True, n_jobs=1, with_stress=False)
```

To get the number of supported characters to know how many embeddings to initialize in your TTS neural network (note: current API supports only IPA phoneme scheme):

```python
tf = TextFrontend(use_phonemes=False)  # if using graphemes for encoding
print(tf.nchars)
# Output: 119

tf = TextFrontend(use_phonemes=True)  # if using phonemes for encoding
print(tf.nchars)
# Output: 236
```

Text encoding:

```python
# Encodes grapheme inputs
tf = TextFrontend(text_cleaners=['english_cleaners'], use_phonemes=False)

text = "Mr. User, this is test sentence to check the performance of phonemizer and text-to-sequence encoding."
print(tf.graphemes_to_phonemes(text, lang='en-us'))  # it still can make G2P
# Output: "m_ˈɪ_s_t_ɚ_._ _j_ˈuː_z_ɚ_,_ _ð_ɪ_s_ _ɪ_z_ _t_ˈɛ_s_t_ _s_ˈɛ_n_t_ə_n_s_ _t_ə_ _tʃ_ˈɛ_k_ _ð_ə_ _p_ɚ_f_ˈoːɹ_m_ə_n_s_ _ʌ_v_ _f_ˈoʊ_n_m_aɪ_z_ɚ_ _æ_n_d_ _t_ˈɛ_k_s_t_-_ _t_ə_-_ _s_ˈiː_k_w_ə_n_s_ _ɛ_ŋ_k_ˈoʊ_d_ɪ_ŋ_."

sequence = tf.text_to_sequence(text, lang='en-us')
print(sequence)
# Output: [36, 32, 42, 43, 28, 41, 2, 44, 42, 28, 41, 5, 2, 43, 31, 32, 42, 2, 32, 42, 2, 43, 28, 42, 43, 2, 42, 28, 37, 43, 28, 37, 26, 28, 2, 43, 38, 2, 26, 31, 28, 26, 34, 2, 43, 31, 28, 2, 39, 28, 41, 29, 38, 41, 36, 24, 37, 26, 28, 2, 38, 29, 2, 39, 31, 38, 37, 28, 36, 32, 49, 28, 41, 2, 24, 37, 27, 2, 43, 28, 47, 43, 6, 43, 38, 6, 42, 28, 40, 44, 28, 37, 26, 28, 2, 28, 37, 26, 38, 27, 32, 37, 30, 7, 1]

print(tf.sequence_to_text(sequence))  # however encoding corresponds only to grapheme representation
# Output: "mister user, this is test sentence to check the performance of phonemizer and text-to-sequence encoding."
```


```python
# Encodes phoneme inputs
tf = TextFrontend(text_cleaners=['english_cleaners'], use_phonemes=True, with_stress=True)

text = "Mr. User, this is test sentence to check the performance of phonemizer and text-to-sequence encoding."
print(tf.graphemes_to_phonemes(text, lang='en-us'))
# Output: "m_ˈɪ_s_t_ɚ_._ _j_ˈuː_z_ɚ_,_ _ð_ɪ_s_ _ɪ_z_ _t_ˈɛ_s_t_ _s_ˈɛ_n_t_ə_n_s_ _t_ə_ _tʃ_ˈɛ_k_ _ð_ə_ _p_ɚ_f_ˈoːɹ_m_ə_n_s_ _ʌ_v_ _f_ˈoʊ_n_m_aɪ_z_ɚ_ _æ_n_d_ _t_ˈɛ_k_s_t_-_ _t_ə_-_ _s_ˈiː_k_w_ə_n_s_ _ɛ_ŋ_k_ˈoʊ_d_ɪ_ŋ_."

sequence = tf.text_to_sequence(text, lang='en-us')
print(sequence)
# Output: [153, 45, 42, 225, 89, 135, 127, 122, 137, 89, 5, 135, 76, 159, 42, 135, 159, 137, 135, 225, 87, 42, 225, 135, 42, 87, 165, 225, 77, 165, 42, 135, 225, 77, 135, 55, 87, 160, 135, 76, 77, 135, 147, 89, 38, 83, 153, 77, 165, 42, 135, 104, 139, 135, 38, 123, 165, 153, 217, 137, 89, 135, 133, 165, 151, 135, 225, 87, 160, 42, 225, 6, 135, 225, 77, 6, 135, 42, 141, 160, 35, 77, 165, 42, 135, 158, 40, 160, 123, 151, 159, 40, 7, 1]

print(tf.sequence_to_text(sequence))  # encoding corresponds to phoneme representation
# Output: "m_ˈɪ_s_t_ɚ_ _j_ˈuː_z_ɚ_,_ _ð_ɪ_s_ _ɪ_z_ _t_ˈɛ_s_t_ _s_ˈɛ_n_t_ə_n_s_ _t_ə_ _tʃ_ˈɛ_k_ _ð_ə_ _p_ɚ_f_ˈoːɹ_m_ə_n_s_ _ʌ_v_ _f_ˈoʊ_n_m_aɪ_z_ɚ_ _æ_n_d_ _t_ˈɛ_k_s_t_-_ _t_ə_-_ _s_ˈiː_k_w_ə_n_s_ _ɛ_ŋ_k_ˈoʊ_d_ɪ_ŋ_."
```

Just cleaning the text:

```python
from text_frontend import clean_text

text = "Mr. User, this is test sentence   to check the performance of text cleaning. It costs $0."
print(clean_text(text, ['english_cleaners']))
# Output: "mister user, this is test sentence to check the performance of text cleaning. it costs zero dollars."
```

For more details read the docs when calling functions.
