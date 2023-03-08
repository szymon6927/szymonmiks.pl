+++
author = "Szymon Miks"
title = "How to make an API request to an AWS microservice that is protected by IAM auth"
date = "2023-04-02"
image = "img/georg-bommeli-ybtUqjybcjE-unsplash.jpg"
categories = [
     "Python", "Software_Development", "AWS"
]
tags = [
    "python",
    "software development",
    "boto3",
    "AWS",
    "cloud services",
    "microservices",
    "apigw",
    "iam auth"
]
draft = false
mermaid = true
+++

## Intro

One of the authorization methods that AWS supports for the API Gateway endpoints is
[IAM authorization](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control-iam.html).

Two things are required to use IAM auth:
- signed request using [Signature Version 4](https://docs.aws.amazon.com/general/latest/gr/signing-aws-api-requests.html)
- `execute-api` permission set up for the client for invoked endpoint

There are other authorization methods available like: `Lambda authorizers` or `JWT authorizers` you can read more about them
[here](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control.html).

In today's blog post, I will show you how to request a microservice that is protected by IAM auth.


## The problem

For the blog post purpose, let's imagine we have two microservices: `Microservice A` and `Microservice B`.
Both of them were built using AWS lambda and API Gateway.
We own `Microservice A`, and some other team owns `Microservice B`.
We want to call `Microservice B` to get the response, it exposes the endpoint `GET /items`, and this endpoint is protected by `IAM auth`.

{{<mermaid>}}
sequenceDiagram
    Microservice A->>+Microservice B: GET /items
    Microservice B ->>+ Microservice B: Authorize the request
    Microservice B ->>+ Microservice A: 200 Response
{{</mermaid>}}


## Solution

```python
import os
from urllib.parse import urlparse
from logging import Logger

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from requests.exceptions import RequestException

class MicroserviceBClientClientError(Exception):
    pass


class MicroserviceBClient:
    def __init__(self, base_url: str, logger: Logger) -> None:
        self._base_url = base_url
        self._logger = logger

    @property
    def auth(self) -> BotoAWSRequestsAuth:
        return BotoAWSRequestsAuth(
            aws_host=urlparse(self._base_url).hostname, aws_region=os.environ["AWS_REGION"], aws_service="execute-api"
        )

    def get_items(self) -> None:
        try:
            self._logger.info("Getting items from MicroserviceB!")
            response = requests.post(
                f"{self._base_url}/items", auth=self.auth
            )
            response.raise_for_status()
            self._logger.info(f"Successful request! Response = {response.json()}")
        except RequestException as error:
            self._logger.error(f"An error occurred during request to `MicroserviceB` service! Error = {error}")
            raise MicroserviceBClientClientError
```

The [aws-requests-auth](https://github.com/davidmuller/aws-requests-auth) does most of the things for us.

We need to provide the hostname of the service we want to call, the AWS region,
and the service - in our case it is `execute-api` as we are working in a serverless lambda environment.

`BotoAWSRequestsAuth` generates the appropriate headers and adds them to the `requests` object.
All we need to do is to add it as a `auth` param to the [requests](https://requests.readthedocs.io/en/latest/) method.

## Summary

It is as simple as that :wink: I hope you enjoyed it.

There are other methods that you can use to make such a request.
The one I showed you is simple and easy.
I have tested it on production, it is working :wink:.
