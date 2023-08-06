# langai-python [![travis](https://api.travis-ci.com/lang-ai/langai-python.svg?branch=master)](https://travis-ci.com/lang-ai/langai-python)

A LangAI API client written in Python.

Check the [API Docs](https://docs.lang.ai) and the [Developer site](https://lang.ai/developers) for more info on how to use and integrate the API.

> To work with the LangAI API, you must have a token. If you don't have a token already, [request an invite](https://lang.ai/developers).

## Installation

Install [`langai-python`](https://www.npmjs.com/package/langai-python) in your python project with pip.

```
pip install -u langai
```


See the example below on how to import and use the LangAI API to analyze intents in new texts. A projectId is required. Check the [`workflow`](https://docs.lang.ai/#workflow) documentation to get an overview of the process.

## Usage

```python
from langai import LangAiClient

lang = LangAiClient("your_token")
params = {
    text: 'your-text',
    projectId: 'your-projectId',
}
result = lang.analyze(**params)
print(result)

```


