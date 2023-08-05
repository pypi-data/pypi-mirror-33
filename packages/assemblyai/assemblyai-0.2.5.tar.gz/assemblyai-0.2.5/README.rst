=====================
assemblyai-python-sdk
=====================


Transcribe audio into text. Recognize made-up words and boost accuracy using custom language models.

- Documentation: https://assemblyai-python-sdk.readthedocs.io
- Issues: https://github.com/assemblyai/assemblyai-python-sdk
- Support: https://docs.assemblyai.com/help/#slack
- Community: https://assemblyaicommunity.slack.com


Getting started
---------------

Run pip install and get an API token from https://assemblyai.com

    pip install assemblyai


Quickstart
----------

Start transcribing:

    import assemblyai

    aai = assemblyai.Client(token='secret-token')

    transcript = aai.transcribe(filename='example.wav')


Get the completed transcript. Transcripts take about half the duration of the
audio to complete.

    while transcript.status != 'completed':
        transcript = transcript.get()

    text = transcript.text


Instead of a local file, you can also specify a url for the audio file:


    transcript = aai.transcribe(audio_url='https://example.com/example.wav')


Custom language models
----------------------

The quickstart example transcribes audio using a generic English model.

In order to boost accuracy and recognize custom words, you can create a custom
model. You can read more about how custom model work
[in the docs](https://docs.assemblyai.com/guides/#custommodels101).

Create a custom model.

    import assemblyai

    aai = assemblyai.Client(token='your-secret-api-token')

    # phrases is a list or words (real or made up) and sentences that you want to recognize
    phrases = ["foobar", "Dirk Gently", "electric monk", "yourLingoHere",
               "perhaps a common phrase here", "and a common response"]

    model = aai.train(phrases)


Check to see that the model has finished training -- models take about six
minutes to complete.

    while model.status != 'trained':
        model = model.get()

Reference the model when creating a transcript.

    transcript = aai.transcribe(filename='/path/to/example.wav', model=model)


Transcribing stereo
-------------------

For stereo audio with two speakers on separate channels, you can leverage
enhanced accuracy and formatting by setting speak_count to 2.

    transcript = aai.transcribe('example.wav', speaker_count=2)


Unformatted text
----------------

To receive transcript text without formatting or punctuation, set the option
format_text to False (default is True).

    transcript = aai.transcribe('example.wav', format_text=False)


Model and Transcript attributes
-------------------------------

Prior models and transcripts can by called by ID.

    model = aai.model.get(id=<id>)
    transcript = aai.transcript.get(id=<id>)

To inspect additional attributes, use `props()`:

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
    >>>  'dict']

The `dict` attribute contains the raw API response:

    model.dict
    transcript.dict

For additional background see: https://docs.assemblyai.com
