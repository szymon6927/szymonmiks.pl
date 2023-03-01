+++
author = "Szymon Miks"
title = "What are architectural drivers in software engineering?"
description = "How to make the right decision when it comes to software architecture?"
date = "2023-03-03"
image = "img/mikail-mcverry--yBvef_mAaQ-unsplash.jpg"
categories = [
     "General", "Architecture"
]
tags = [
    "software development",
    "architectural drivers",
    "ADR"
]
draft = false
+++

## Intro

There are many definitions of **software architecture**.

The definition that appeals to me the most is **a set of made decisions**.
These decisions are driven by something right? That is exactly what **architectural drivers** are.


This is something that influences our decisions about architecture.
It shapes our software.
For example, we chose a relational database or some library for logging,
or we decided to follow [hexagonal architecture](/p/hexagonal-architecture-in-python/) principles - each of them has an influence on the architecture.

**Architectural drivers** is a set of things that shape, influence, and drive the software architecture.


## Classes of architectural drivers

We identify 5 different classes of architectural drivers. Here is a short description of each of them.

### Functional requirements

It is a list of functions that our software needs to provide.
We like to call it **business logic**.

For example, our system needs to send an email after successful account creation.
This potentially leads us to choose some email services providers like [AWS SES](https://aws.amazon.com/ses/) or others.


### Quality attributes

This includes all technical elements like:
- scalability
- extensibility
- security
- auditability
- configurability
- observability
- testability

and many others :wink:.


### Project's constraints

Each project is different, the team size, the team's experience, budget, deadline, etc.
This is also something that influences our architecture.

Let me give you an example from Python's world.

If there is a short deadline and our team knows Django very well. We won't choose some new framework that no one knows.
But instead, most probably we will choose the well-known framework that we as a team feel comfortable with.

Another example: If the project's budget is low, we won't choose a very expensive CI/CD tool.

### Conventions

These are all the rules that our organization/team follows to have cohesive solutions.

Example: If our organization uses `pytest` in all projects, and this is standard and common practice.
We should not use `unittest` library without having strong indications and reasoning behind it.

### Project's goals

For example, our project might be some company internal tool or MVP.

If it is a company internal tool we might not be interested in a high-performance database there or an auto-scaling mechanism.
Or if it is an MVP we might want to do some shortcuts and use an in-memory database, just to prove that something is working as we expect.

An example from the DDD's world.
If it is a "generic" or "supporting" domain, we might want to use some already existing tool on the market or order the development from someone else - freelancers or software houses.


## Documenting the decisions

Some time ago, I wrote an article about [ADR](/p/what-is-an-adr/).
This is one of the ways how you can document your architectural decisions.
In my opinion, the easiest and cheapest one. I recommend it.
If you have not heard anything about ADRs I encourage you to read my article :wink:.


## Discovering the architectural drivers

It is important to discover as many architectural drivers as we can.
Especially at the beginning of the project.
Correctly discovered might save us money and time.
We make sure that we build what is intended to be built.
It makes us closer to the solution and allows us to narrow down the area of the unknown.

The source of the information about them is business stakeholders.
They know what needs to be done, what features should be there, what will be the number of users on live, etc.

How we can get those pieces of information from them?

One of the techniques to discover the architectural drivers is  [stakeholder mapping](https://en.wikipedia.org/wiki/Stakeholder_analysis).

![example stakeholders matrix from wikipedia](https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Stakeholders_matrix.svg/600px-Stakeholders_matrix.svg.png#center)

---

The diagram above is called the stakeholders' matrix.
In this diagram, we can see who has the highest interest and the highest impact on the project, also we can see who has the lowest interest and impact on the project.

With that knowledge, we know that different people will have different perspectives on the project.
Most probably the project’s investor will be interested in features and delivery time, while CTO might be more interested in conventions and standards that are present in the company.

This is our role to discover the most important **architectural drivers** and reconcile the interests of the most important business stakeholders.
Be a partner for business stakeholders.


## Summary

Everything is a trade-off.
Especially in the IT industry :wink:.

Sometimes the **architectural drivers** may exclude each other.
High availability is against a low project budget.

We can not say that solution X is better than solution Y.
Everything has its own context.

By discovering the **architectural drivers** we may achieve a "good enough" situation within the current context.
It does not mean that is it the best option ever.
Instead, it means that it is the best option for the current situation, requirements, constraints, etc.

Making a decision is hard, making a good decision is even harder.
I hope I showed you how you can minimize the risk of making a wrong decision about your software architecture.

I hope you enjoyed it.
Let me know how you make decisions about software architecture, and what systems/tools/techniques do you use.

## Additional Resources

- [Software Architecture for Developers](https://softwarearchitecturefordevelopers.com/)
- [Software Architecture in Practice](https://www.amazon.com/Software-Architecture-Practice-SEI-Engineering/dp/0136886094)
- [Design It!](https://www.amazon.com/dp/1680502093/)
