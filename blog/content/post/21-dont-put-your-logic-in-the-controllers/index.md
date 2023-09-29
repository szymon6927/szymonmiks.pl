+++
author = "Szymon Miks"
title = "Don't put your business logic in the controllers"
description = "A brief explanation of why adding the business logic to the controller is not a good idea. Overview of other options we have."
date = "2023-09-10"
image = "img/kier-in-sight-archives-4bhhwmsYl-c-unsplash.jpg"
categories = [
     "Python", "Software_Development", "Architecture", "Testing"
]
tags = [
    "python",
    "software development",
    "architecture",
    "business logic",
    "application design",
    "good practises"
]
draft = false
+++

## Intro

In the world of **WEB API** development with Python, maintaining clean and maintainable code is paramount.
One common pitfall to avoid is mixing your business logic with your **controllers/views/handlers**.

I mentioned **handlers** for a reason.
Serverless hype means that no one uses controllers anymore right? :smile:

In this blog post, we'll explore why it's crucial not to put your business logic in the **controllers/views/handlers**
of your application and discuss alternative approaches to keep your codebase well-organized.


## What are controllers?

Depending on where you're coming from and what your project looks like,
I'm assuming you're using one of these three - controllers, views, handlers.

If your project is built using Django or Flask probably you are using **views**.

If your project uses a Serverless stack such as AWS Lambda + API Gateway, you are probably using **handlers**.

If your project is built using [litestar](https://litestar.dev/) then you have **controllers**.

I mention all of these to tell you that it is just a naming because the general intention is the same.

Controllers/Views/Handlers play a vital role in the request-response cycle of a web application.
They are responsible for handling incoming HTTP requests, routing them to the appropriate functions, and returning HTTP responses.
**That's it, nothing more!**

Let’s establish that for the purpose of this article, I will be using **controllers** as a name.
The reason is simple - this name is not specific to any environment or framework and is commonly used in our industry.


## What is business logic?

Business logic represents the core functionality of your application.
It includes tasks like data validation, calculations, database interactions, and decision-making processes.
Business logic is what makes your application unique and valuable.

## The problems with mixing controllers and business logic

When you put your business logic inside your controllers, several issues can arise:

- Reduced code readability and maintainability.
- Difficulty in testing individual components.
- Violation of the Single Responsibility Principle (SRP).
- Potential code duplication.


To illustrate this, we will implement a simple **article creation** endpoint.

The requirements are as follows, nothing really complicated, but I think they are good enough for the example purpose:
- The number of tags of the article may not be bigger than 10
- The title of the article may not be smaller than 5 words
- The content of the article may not be smaller than 50 words!
- The article has to have at least one category!
- The article has to have at least 2 reviewers
- The e-mail addresses of reviewers need to be valid e-mail addresses
- The article should be created with `DRAFT` status by default

Take a look at the code below:

```python
# blog/examples/src/business_logic_in_controllers/example1.py

@app.post("/articles", status_code=201)
async def create_article(
    request: CreateArticleRequest,
    repository: Annotated[ArticleRepository, Depends(get_article_repository)]
) -> JSONResponse:
    if len(request.tags) > 10:
        raise HTTPException(status_code=400, detail="Number of tags may not be bigger than 10!")

    if len(request.title.split(" ")) < 5:
        raise HTTPException(status_code=400, detail="Title may not be smaller than 5 words!")

    if len(re.findall(r"\w+", request.content)) < 50:
        raise HTTPException(status_code=400, detail="Content of the article may not be smaller than 50 words!")

    if len(request.categories) < 1:
        raise HTTPException(status_code=400, detail="Article has to have at least one category!")

    reviewers = []
    for email in reviewers:
        try:
            validated_email = validate_email(email, check_deliverability=False)
            reviewers.append(validated_email)
        except EmailNotValidError:
            raise HTTPException(status_code=400, detail=f"Provided reviewer email address `{email}` is not correct")

    if len(reviewers) < 2:
        raise HTTPException(status_code=400, detail="Article has to have at least 2 reviewers")

    article_id = EntityId.new_one()
    article = Article(
        id=article_id,
        title=request.title,
        content=request.content,
        created_at=datetime.utcnow(),
        status=Status.DRAFT
    )

    repository.save(article)

    for reviewer in request.reviewers:
        notify_reviewers(reviewer)

    return JSONResponse(content={}, headers={"Location": f"/articles/{article.id}"})


def notify_reviewers(reviewer: str) -> None:
    print(f"Notifying reviewer {reviewer} that a new article is awaiting his review!")
```

After reading this code snippet, what do you feel? There are a lot of things happening there right?

- Reading this code is hard
- Testing is hard
- Maintaining it in a longer time perspective is also hard
- Adding new features - the same
- What if we would want to add the article via the CLI command? Not possible at all!

:warning: **REMINDER**  - controllers should be only responsible for handling incoming HTTP requests,
routing them to the appropriate functions, and returning HTTP responses


## What are the alternative approaches?

If you've gotten to this point, you probably know that there are other alternative approaches.

Adding everything to the controllers is not the only option that we have :smile: Thanks to God!

One approach to separate business logic is to create a **service layer**.
The second is to use **command handlers**.

About both of them, you can read on my blog. I compared them.
You can read about it [here (Services vs Command Handlers - choosing the right approach in your application)](/p/services-vs-command-handlers/)!
Code examples are included there too.

To fill the gap I also created an article about [How to implement CommandBus in Python](/p/how-to-implement-commandbus-in-python/).


## Benefits of separating business Logic

- Enhanced code readability and maintainability
- Easier testing of business logic in isolation
- Better adherence to SRP
- Reduced risk of code duplication

## Implementation tips

When implementing the chosen approach, consider the following tips:

Organize your codebase into clear directories and modules.
Ensure that controllers remain lightweight and only handle HTTP-related tasks.
Write comprehensive unit tests for your business logic components.


## Summary

In conclusion, keeping your business logic out of your controllers is a fundamental practice in **WEB API** development.
It leads to cleaner, more maintainable code and facilitates testing and scalability.
By adopting alternative approaches like service layers, command handlers, or query handlers you can achieve a well-structured and robust codebase for your applications.

Share your thoughts and experiences with separating business logic in the comments below.
Have you faced any challenges or discovered unique solutions?
Let’s discuss it!
