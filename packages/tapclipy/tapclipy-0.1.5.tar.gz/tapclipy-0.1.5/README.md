[![PyPI version](https://badge.fury.io/py/tapclipy.svg)](https://badge.fury.io/py/tapclipy) [![https://img.shields.io/badge/license-Apache%202.0-blue.svg](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

# TapCliPy
Python Client Library for [TAP](https://github.com/heta-io/tap)

### Installation

Install with pip:

```bash
> pip install tapclipy
```

### Basic Example

```python

from tapclipy import tap_connect

# Create TAP Connection
tap = tap_connect.Connect('http://tap.yourdomain.com')

# Get and print the Current Schema
tap.fetch_schema()
for query,type in tap.schema_query_name_types().items():
    print("{} >> {}".format(query, type))
print("----------------------------------------------")

# Analyse some text for some basic metrics
query = tap.query('metrics')
text = "This is a very small test of TAP. It should produce some metrics on these two sentences!"
json = tap.analyse_text(query, text)

print()
print("METRICS:\n", json)

```

should output:

```

visible >> StringResult
clean >> StringResult
cleanPreserve >> StringResult
cleanMinimal >> StringResult
cleanAscii >> StringResult
annotations >> SentencesResult
vocabulary >> VocabResult
metrics >> MetricsResult
expressions >> ExpressionsResult
syllables >> syllables
spelling >> SpellingResult
posStats >> PosStatsResult
reflectExpressions >> ReflectExpressionsResult
moves >> StringListResult
----------------------------------------------

METRICS:
 {'data': {'metrics': {'analytics': {'words': 17, 'sentences': 2, 'sentWordCounts': [8, 9], 'averageSentWordCount': 8.5}}}}

Process finished with exit code 0

```

### Currently available queries

| Query | Return Type |
|-------|-------------|
| visible | `StringResult` |
| clean | `StringResult` |
| cleanPreserve | `StringResult` |
| cleanMinimal | `StringResult` |
| cleanAscii | `StringResult` |
| annotations | `SentencesResult` |
| vocabulary | `VocabResult` |
| metrics | `MetricsResult` |
| expressions | `ExpressionsResult` |
| syllables | `syllables` |
| spelling | `SpellingResult` |
| posStats | `PosStatsResult` |
| reflectExpressions | `ReflectExpressionsResult` |
| moves | `StringListResult` |