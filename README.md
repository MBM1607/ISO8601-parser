# ISO8601-parser
A python ISO8601 format datetime parser.

## Introduction
I wrote this parser for python-discord winter code jam 6 qualifier. The parses accepts both extended and basic formats of datetimes.
The only formats excluded from the parser are those that couldn't be converted to a direct equivalent in datetime.datetime.
like the YYYY-WW format or the YYYY-MM format.

## Usage
```python
from qualifier import parse_iso8601

parse_iso8601("2012-12-12T12:12:12.132")
```

## Testing
To run the test you will need [pytest](https://docs.pytest.org/en/latest/) library.
Install pytest by running
```pip install pytest```

Run the the test with the following command
```python -m pytest```

## License
[MIT](https://choosealicense.com/licenses/mit/)
