+++
author = "Szymon Miks"
title = "What is an ADR?"
description = ""
date = "2022-02-24"
image = ""
categories = [
    "Software Development", "Architecture"
]
tags = [
    "architecture", "software development", "adr"
]
draft = false
+++

How many times you made a decision in the project and after a couple of months you forgot why you or someone else did it? From my perspective and experience it happened many times to me. There is always a pressure to deliver new features, and there is always a deadline with it. Because of that I believe everyone had a situation like: "hmm why I decided to did it in that way".

BTW those things are called "architectural drivers" but I will talk about them in a separate blog post.

Back to our main topic, there is a solution for such problems and it's called ADR, and in today's post I would like to do a brief intro about it.

## ADR

ADR is an acronym of Architecture Decision Record and it's a way of documenting changes in our architecture. It's a pure text file with no pre-defined format or schema. 

The most popular structure/template is proposed by Michael Nygard in 2011, [here you can find his blog post about it.](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions). I was also following his approach (maybe not all of it, but you will see it in the example section) in my project.

The template comprises four parts:

- Context - what this decision is about
- Decision/Solution - the decision made on how to solve the problem
- Consequences - the result of making a given decision
- Status - whether a decision has been made, withdrawn, or is it just a proposal

## ADR - good practises

- the record describes only one decision
- the record contains when this decision has been made
- record explains the reason behind this decision
- the record must be immutable
- all team members use ADR
- source code can contain a reference to the corresponding ADR
- records should be numbered

## ADL

The place where all the records are - is called ADL - architecture decision log.

It can be:

- git project repository (as I used in my project)
- Jira
- Google Drive
- Confluence

Use whatever works for your project/team/company. The most important thing is that every team member should be aware of where ADL is and how to access it.

## Examples

I would like to show you some examples from my project. I used git repo as my ADL and I was not strictly following Michael Nygard's template, you will see this in the following examples. Mainly because I didn't feel the need to do this, and I didn't want to force it. It should be easy to use for others and adjusted to our requirements.

![Screenshot_2021-04-04_at_15.05.34.png](Screenshot_2021-04-04_at_15.05.34.png)

`adr-001-database_choice.md`

```markdown
Context: At this stage of project evolution we don't know the data schema, and we don't know amount and format 
of data returned from ML models.

Solution: We decided to use `mongodb` as our database

Comment: in our opinion it is the best db for start, then if it will be required we can change it something different.
```

`adr-002-framework_choice.md`

```markdown
Context: We need fast and flexible python web framework

Solution: We decided to use [Starlette](https://www.starlette.io/)

Comment: this framework support async operations and give us flexibility. We also considered FastAPI but in reality it's
a wrapper for Starlette and it has a few features which are not important/usefull to us.
```

Context: We need fast and flexible python web framework

Solution: We decided to use [Starlette](https://www.starlette.io/)

Comment: this framework support async operations and give us flexibility. We also considered FastAPI but in reality it's
a wrapper for Starlette and it has a few features which are not important/usefull to us.
```markdown
Context: We need fast and flexible python web framework

Solution: We decided to use [Starlette](https://www.starlette.io/)

Comment: this framework support async operations and give us flexibility. We also considered FastAPI but in reality it's
a wrapper for Starlette and it has a few features which are not important/usefull to us.
```

`adr-010-account-id-in-events.md`

```markdown
Context: We want to have history of user's actions in the platform

Solution: We are passing `account_id` to all events which are happening in the platform, based on that we will be
able to easily filter all events related to the account.
```

# Final thoughts

I really encourage you to use ADRs. From my perspective it's useful and it really pays off. There are a lot of benefits and will make our work easier. If you have any questions are would like to talk about ADR's, don't hesitate to ping me directly or write a comment 😉