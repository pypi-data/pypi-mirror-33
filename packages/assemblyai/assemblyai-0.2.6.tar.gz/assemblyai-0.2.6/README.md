# assemblyai

![](https://img.shields.io/badge/Python-2.7%2C%203.5%2C%203.6-blue.svg)
[![](https://img.shields.io/pypi/v/assemblyai.svg)](https://pypi.org/project/assemblyai/)
[![](https://img.shields.io/travis/AssemblyAI/assemblyai-python-sdk.svg)](https://travis-ci.org/AssemblyAI/assemblyai-python-sdk/builds)
[![](https://pyup.io/repos/github/AssemblyAI/assemblyai-python-sdk/shield.svg)](https://pyup.io/repos/github/AssemblyAI/assemblyai-python-sdk)
[![](https://codecov.io/gh/AssemblyAI/assemblyai-python-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/AssemblyAI/assemblyai-python-sdk)
[![](https://api.codeclimate.com/v1/badges/a4fbbc5b564389549af7/maintainability)](https://codeclimate.com/repos/5afb734416a00d6f410000a9/maintainability)
[![](https://img.shields.io/badge/Slack-community-71D4DF.svg)](https://docs.assemblyai.com/help/#slack)
<!-- [![](https://readthedocs.org/projects/assemblyai-python-sdk/badge/?version=latest)](https://readthedocs.org/projects/assemblyai-python-sdk) -->

Accurately recognize speech in your application with AssemblyAI.

You can also train custom models to more accurately recognize speech in your application, and expand vocabulary with custom words like product/person names.

Documentation:
- https://docs.assemblyai.com
- https://assemblyai-python-sdk.readthedocs.io

Slack community: https://docs.assemblyai.com/help/#slack

Issues: https://github.com/assemblyai/assemblyai-python-sdk


## Getting started

Run pip install and email support@assemblyai.com for an API token (we reply at most within a few hours).

```shell
pip install assemblyai
```


## Quickstart

Start transcribing:

```python
import assemblyai

aai = assemblyai.Client(token='your-secret-api-token')

transcript = aai.transcribe(filename='/path/to/example.wav')
```

Get the completed transcript. Transcripts take about half the duration of the
audio to complete.

```python
while transcript.status != 'completed':
    transcript = transcript.get()

text = transcript.text
```

Instead of a local file, you can also specify a url for the audio file:

```python
transcript = aai.transcribe(audio_url='https://example.com/example.wav')
```


## Custom models

The quickstart example transcribes audio using a generic English model.

In order to boost accuracy and recognize custom words, you can create a custom
model. You can read more about how custom model work
[in the docs](https://docs.assemblyai.com/guides/#custommodels101).

Create a custom model.

```python
import assemblyai

aai = assemblyai.Client(token='your-secret-api-token')

# phrases is a list or words (real or made up) and sentences that you want to recognize
phrases = ["foobar", "Dirk Gently", "electric monk", "yourLingoHere",
           "perhaps a common phrase here", "and a common response"]

model = aai.train(phrases)
```

Check to see that the model has finished training -- models take about six
minutes to complete.

```Python
while model.status != 'trained':
    model = model.get()
```

Reference the model when creating a transcript.

```python
transcript = aai.transcribe(filename='/path/to/example.wav', model=model)
```


## Transcribing stereo audio with two speakers on different channels

For stereo audio with two speakers on separate channels, you can leverage
enhanced accuracy and formatting by setting speak_count to 2.

```python
transcript = aai.transcribe('example.wav', speaker_count=2)
```


## Transcribing without formatted text

To receive transcript text without formatting or punctuation, set the option
format_text to False (default is True).

```python
transcript = aai.transcribe('example.wav', format_text=False)
```


## Model and Transcript attributes

Prior models and transcripts can be called by ID.

```python
model = aai.model.get(id=<id>)
transcript = aai.transcript.get(id=<id>)
```

To inspect additional attributes, use `props()`:

```Python
model.props()

>>> ['headers',
>>>  'id',
>>>  'status',
>>>  'name',
>>>  'phrases',
>>>  'warning',
>>>  'dict']

transcript.props()

>>> ['headers',
>>>  'id',
>>>  'audio_url',
>>>  'model',
>>>  'status',
>>>  'warning',
>>>  'text',
>>>  'text_raw',
>>>  'confidence',
>>>  'segments',
>>>  'speaker_count',
>>>  'format_text',
>>>  'dict']
```

The `dict` attribute contains the raw API response:

```Python
model.dict
transcript.dict
```

For additional background see: https://docs.assemblyai.com


## Troubleshooting

Enable verbose logging by enabling the Client debug option:

```Python
import assemblyai

aai = assemblyai.Client(debug=True)
```

More options to get unstuck:

- Create an [Issue](https://github.com/AssemblyAI/assemblyai-python-sdk/issues)
- Join us on [Slack](https://docs.assemblyai.com/help/#slacksupport)
- Send us an [email](mailto:support@assemblyai.com)


## Development

Install dev requirements, install from source and run tests.

```shell
pip install -r requirements_dev.txt
python setup.py install
tox
```


## Contributing

Bug reports and pull requests welcome.


## Release notes

**0.2.6** - Bug fixes, logging improvements, and cleanup