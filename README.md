# Barsic Bot Service

A bot for interacting with the "Barsic API" service.

* **Application Language:** Python 3.12
* **Supported Communication Protocols:** REST API
* **Infrastructure Dependencies:** Redis
* **System Package Dependencies:** None
* **PostgreSQL Extension Dependencies:** None
* **Environment Type:** development
* **Minimum System Requirements:** 1 CPU, 1Gb RAM

## Service Support

Development team:

* Ivan Bazhenov (*[@sendhello](https://github.com/sendhello)*)

## Required Methods to Launch the Service

### Launching the Service
```commandline
# on the root
python main.py
```

## Additional Service Methods

### Description of ENV Variables


| Environment Variable Name | Possible Value | Description                         |
|:--------------------------|----------------|:------------------------------------|
| DEBUG                     | False          | Debug mode                          |
| PROJECT_NAME              | Barsic         | Service name (displayed in Swagger) |
| REDIS_HOST                | redis          | Redis server name                   |
| REDIS_PORT                | 6379           | Redis server port                   |
