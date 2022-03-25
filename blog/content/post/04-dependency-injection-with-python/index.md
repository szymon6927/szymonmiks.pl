+++
author = "Szymon Miks"
title = "Dependency injection with Python, make it easy!"
description = "How to use dependency injection pattern with Python"
date = "2021-04-14"
image = "img/chris-ried-ieic5Tq8YMk-unsplash.jpg"
categories = [
     "Software_Development", "Python"
]
tags = [
    "python", "di", "dependency injection", "kink"
]
draft = false
canonicalUrl = "https://www.netguru.com/blog/dependency-injection-with-python-make-it-easy"
+++

As a software engineer, your objective is to built software in a way it is modular and easy to extend. 
There are a few general factors that one should take into consideration:

- separation of concerns
- low coupling
- high cohesion

Dependency Injection is a technique that favours these factors and in this blog post, 
I will try to explain why this is the case and how to use dependency injection with Python to improve your daily life and produced software.

It is a known fact DI is not widely used inside Python mostly because of its scripting nature 
but you as an experienced developer should already know that Python is not only a scripting language 
but is widely used in professional software development as well. So give me a chance to convince you :wink:

**Dependency injection** is a technique built on the top of the **Inversion of Control**. 
The main idea is to separate the construction and usage of objects.

Let's consider the following example:

```python
# bad case
class S3FileUploader(FileUploader):
    def __init__(self, bucket_name: str) -> None:
        self._bucket_name = bucket_name
        self._sdk_client = boto3.client("s3") # our dependency
```

`S3FileUploader` is an implementation of `FileUploader` interface and is using `boto s3 sdk client`.
This relationship is called a **"dependency"**. 

In the given example `boto3.client("s3")` construction is hardcoded inside `S3FileUploader` initialiser. 
Which might be an indication of a bad design.

The solution here is to delegate the responsibility related to initialising an object and inject the object initialised this way as our dependency.

## Global state

Let’s be honest, the example above is not the worst-case scenario. 
Many times I've seen examples where a class depended on something from a global state (been there, done that, learnt my lesson :sweat_smile: ).

```python
# worst case scenario
S3_SDK_CLIENT = boto3.client("s3")

class S3FileUploader(FileUploader):
    def __init__(self, bucket_name: str) -> None:
        self._bucket_name = bucket_name

    def upload_files(self, files: List[str]) -> None:
        for file in files:
            ...
            S3_SDK_CLIENT.upload_file(...)
            ...
```

**Please do not rely on a global state** :exclamation:

There are plenty of conversations on the internet talking about why this is bad. 
Allow me to explain why this is not a good idea:

- it breaks encapsulation - any other object can change the state of it
- testing is much harder - requires a lot of mocks flying around

## Dependency injection library

Let's revisit our previous example and apply the dependency injection technique.

```python
class S3FileUploader(FileUploader):
    def __init__(self, bucket_name: str, s3_sdk_client: S3SdkClient) -> None:
        self._bucket_name = bucket_name
        self._client = s3_sdk_client # this is injected now!
```

Isn't it better? Now it's clearly visible what is required for this class to work. 

To achieve this we will need some dependency injection library. 
In all of my projects I use kink ([https://github.com/kodemore/kink](https://github.com/kodemore/kink)) - it's a library created by my friend :wink:

In my opinion, it's a very flexible, friendly, and easy-to-use Python library. 
I encourage you to check out the GitHub page.

### Examples

#### Setup

I always follow the convention where all my DI definitions are inside a file called `bootstrap.py`

This is something that I came up with during a conversation with one of my friends, 
so if you have any better approaches, please let me know, I'm open to discussion.

```python
# bootstrap.py

from kink import di
...

def bootstrap_di() -> None:
    logger = create_logger(os.getenv("LOG_LEVEL", "INFO"))
    app_config = AppConfig()
    aws_factory = AWSClientFactory(app_config)

    secret_manager_sdk_client = aws_factory.secret_manager_sdk_client()

    di[Logger] = logger
    di[AppConfig] = app_config

    di[SecretManagerSdkClient] = secret_manager_sdk_client
    di[S3SdkClient] = aws_factory.s3_sdk_client()
    di[S3SdkResource] = aws_factory.s3_sdk_resource()

    di[MongoClient] = lambda _di: get_database_connection(app_config, secret_manager_sdk_client)
    di[Database] = lambda _di: _di[MongoClient].get_database("test_db")
    di[UserDbal] = lambda _di: MongoUserDbal(_di[Database])
```

Then in the main project directory inside `__init__.py` I invoke the above function.

```python
# __init__.py

from di_example.bootstrap import bootstrap_di

bootstrap_di()
```

So right now I'm sure that all of my defined dependencies will be registered inside the dependency injection container.

In the case of kink, the dependency injection container is like a Python dict object. 
So you can add new dependencies as you are adding new values to the Python dict which is a cool feature in my opinion.

Also, you can register your dependencies in two ways:

- by type
- by name

So you can do both:

```python
from kink import di
...

di["s3_sdk_client"] = aws_factory.s3_sdk_client()
# and
di[S3SdkClient] = aws_factory.s3_sdk_client()
```

Mainly I'm using the second one because I'm a fan of typing in Python :wink:

As you have seen some of my definitions inside `bootstrap_di` function are using the lambda function. 
It's because **kink** supports on-demand service creation. 
It means that the creation of our dependency will not be executed until it is requested.


Ok, that's all when it comes to setting up our DIC, it's pretty simple, isn't it?

#### Usage

Ok, all of our services/dependencies are defined and waiting for usage. Let see how we can apply this to our code!

```python
from kink import inject
...

@inject
class S3FileReader(FileReader):
    def __init__(self, bucket_name: str, s3_sdk_client: S3SdkClient, logger: Logger) -> None:
        self._bucket_name = bucket_name
        self._client = s3_sdk_client # this is injected now!
        self._logger = logger # this is injected now!
```

We used the `@inject` decorator which is doing auto wiring of our dependencies. 
Generally speaking, auto wiring is a functionality that checks what's inside the DIC, 
and then if the type or name matches with what is defined inside the object's initialiser 
then the **kink** will do the job and will inject exactly what is needed.

Simple, right? This is called `constructor injection` but with kink, we can also do the same with functions. 
Let's consider another example.

```python
from kink import inject
...

@inject
def example_lambda_handler(
    event: LambdaEvent,
    context: LambdaContext,
    app_config: AppConfig, # this is injected
    s3_sdk_client: S3SdkClient, # this is injected
    secret_manager_sdk_client: SecretManagerSdkClient, # this is injected
    logger: Logger, # this is injected
) -> Dict[str, str]:
    logger.debug(f"Event = {event}")
    logger.debug(f"Context = {context}")
```

Again the rules are the same as for `constructor injection`, kink will do the job and will resolve our dependencies automatically.

## Benefits of using DI

- It's much easier to follow SRP (Single Responsibility Principle)
- The code is more reusable - you can inject your services in many places
- It's much easier to test - you can inject mocks or test doubles of your dependencies
- The code is more readable - you are looking only at behaviors of your components
- It can improve the modularity of your application

And much more ...

## Problems with DI

DI will not resolve all the problems automatically for you. 
As a developer, you have to be aware of the responsibilities and roles of your components.

### There are far too many dependencies.

The main problem is the greed of our components. 
So with an easy way to inject dependencies we are injecting "almost everything" into our component. 
What do you think, is this component doing only one thing? 
I will tell you - if it needs to be aware of so many dependencies then it's definitely not doing one thing, this is against SRP. 
That's another indicator of bad design but we don't see it at first glance because we are happy with the ease of use of our **DIC**.

**Greedy components should be refactored!**

Consider the following example:

```python
from kink import inject
...

@inject
def example_lambda_handler(
    event: LambdaEvent,
    context: LambdaContext,
    app_config: AppConfig,
    s3_sdk_client: S3SdkClient,
    secret_manager_sdk_client: SecretManagerSdkClient,
    dynamodb_sdk_client: DynamoDBSdkClient,
    step_functions_sdk_client: StepFunctionsSdkClient,
    mongo_user_dbal: UserDbal,
    logger: Logger,
) -> Dict[str, str]:
    logger.debug(f"Event = {event}")
    logger.debug(f"Context = {context}")
```

It's obvious, this controller does not have one responsibility, this is typical DI abuse. 
The above controller needs to be aware of many dependencies and has to handle many aspects of the business logic. 
Such example should be considered a bad design and DI misuse.

As it is with everything in life if you misuse the DI you can get your project in trouble. 
So in the end, you will end up with less readable code, 
it will be more difficult to manage, and you will lose all the benefits that I mentioned above. 
The final result will be counterproductive. 

I would like to mention Uncle Bob's tweet, 
pretty old, but I think it explains it better than everything that I can bring you to the table.

{{< twitter_simple 308980513929035776 >}}

Original link:
[https://twitter.com/unclebobmartin/status/308980513929035776](https://twitter.com/unclebobmartin/status/308980513929035776)

## Other libraries

On the Python market, there are few other libraries for DI which look promising.

- [https://github.com/alecthomas/injector](https://github.com/alecthomas/injector)
- [https://github.com/ets-labs/python-dependency-injector](https://github.com/ets-labs/python-dependency-injector)

## Links

- [https://github.com/kodemore/kink](https://github.com/kodemore/kink)
- [https://en.wikipedia.org/wiki/Dependency_injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [https://martinfowler.com/articles/injection.html](https://martinfowler.com/articles/injection.html)

## Summary

I hope the main idea behind DI is more clear for you after this blog post. 
And I hope you see the added value of this. I encourage you to try **kink** and DI :sunglasses:

If you have any question/thoughts/comments please don't hesitate to ping me :wink:

Most of the code examples above I took either from my personal or commercial projects. 
But if you would like to check the DI usage in a wider context, and within some real problem, 
you can visit my project on GitHub 
[https://github.com/szymon6927/surebets-finder/tree/master](https://github.com/szymon6927/surebets-finder/tree/master) - I used DI with **kink** there.

**PS.**
This post has been also published on my company's blog (https://www.netguru.com/blog/dependency-injection-with-python-make-it-easy)
