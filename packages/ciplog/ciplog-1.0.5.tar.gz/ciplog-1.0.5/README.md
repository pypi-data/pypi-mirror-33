# CipLog

CipLog is an easy Python package that used for you write your logs.

CipLog has three types of log, **info**, **warning** and **error**

CipLog supports python 3+.

# Examples

## Install

> Under your virtualenv do:  

```
$ pip install ciplog
```

## Getting Started

You can set a service name and a log path or use default.
````python
from ciplog import  CipLog

log = CipLog(service_name='news-api', log_path='/your/log/path')

````

### Info
```python
from ciplog import CipLog

log = CipLog()

log.info(200, 'news', 'news that successfully registered.')

```

### Warning
```python
from ciplog import CipLog

log = CipLog()

log.warning('AB456*', 'news', 'The unicode is not defined.')
```

### Error
```python
from ciplog import CipLog

log = CipLog()

log.error('UX3023', 500, 'news', 'Service is timeout.')

```

## Upload Package
```bash
$ python setup sdist upload
```


## Release History  
* 1.0.5:
    * CHANGE: write with json in file.
    * ADD: status code 400.
* 1.0.4:
    * CHANGE: add error dict.
    * CHANGE: add realese history and upload package in README.
* 1.0.3
    * FIX: typing correct service name.
* 1.0.2
    * ADD: add validate_status_http().
    * ADD: add create_folder().
* 1.0.1
    * CHANGE: log format.
* 1.0.0
  * start of the projects with basic configurations.
