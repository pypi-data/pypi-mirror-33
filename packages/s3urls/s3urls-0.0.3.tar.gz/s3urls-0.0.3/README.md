# S3urls

Parse and build [Amazon S3](https://aws.amazon.com/s3/) URLs.

## Usage

### Parse S3 URLs

```Python
from s3urls import parse_url

>>> parse_url('https://my-bucket.s3.amazonaws.com/my-key/')
{'bucket': 'my-bucket', 'key': 'my-key/'}

>>> parse_url('https://s3-eu-west-1.amazonaws.com/my-bucket/my-key/')
{'bucket': 'my-bucket', 'key': 'my-key/'}

>>> parse_url('s3://my-bucket/my-key')
{'bucket': 'my-bucket', 'key': 'my-key/'}

>>> parse_url('s3://user@my-bucket/my-key')
{'bucket': 'my-bucket', 'key': 'my-key/', 'credential_name': 'user'}
```

### Build S3 URLs

```Python
from s3urls import build_url

>>> build_url('s3', 'my-bucket', 'my-key/')
's3://my-bucket/my-key/'

>>> build_url('s3', 'my-bucket', 'my-key/', credential_name='user')
's3://user@my-bucket/my-key/'

>>> build_url('bucket-in-path', 'my-bucket', 'my-key/')
'https://s3.amazonaws.com/my-bucket/my-key/'

>>> build_url('bucket-in-path', 'my-bucket', 'my-key/', region='eu-west-1')
'https://s3-eu-west-1.amazonaws.com/my-bucket/my-key/'

>>> build_url('bucket-in-netloc', 'my-bucket', 'my-key/')
'https://my-bucket.s3.amazonaws.com/my-key/'
```
