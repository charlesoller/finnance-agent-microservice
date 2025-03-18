![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Mantine](https://img.shields.io/badge/Mantine-ffffff?style=for-the-badge&logo=Mantine&logoColor=339af0)
![React Query](https://img.shields.io/badge/-React%20Query-FF4154?style=for-the-badge&logo=react%20query&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-5469d4?style=for-the-badge&logo=stripe&logoColor=ffffff)
![ChatGPT](https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AmazonDynamoDB](https://img.shields.io/badge/Amazon%20DynamoDB-4053D6?style=for-the-badge&logo=Amazon%20DynamoDB&logoColor=white)
![ESLint](https://img.shields.io/badge/ESLint-4B3263?style=for-the-badge&logo=eslint&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

# Finnance - An AI-Integrated Personal Finance Platform
Live Link: [Finnance](https://www.myfinnance.com/)

### Overview
Finnance integrated agentic AI with the OpenAI API into your finances through the use of Stripe Financial Connections. The user is able to monitor their finances across multiple institutions and accounts in one centralized location, and ask questions about them with their own personal advisor. Finn, the AI agent, has the context of what transaction or account you're talking about, and has extensive capabilities, such as producing graphs, searching the web, calculating exact compound interest, and communicating with external APIs. All of this is presented with a well-designed and pleasing UI, to help users better understand and take control of their finances.

Finnance began as an app to exercise the skills I had learned in my AWS Solutions Architect Associate exam, grew to an idea for a novel new personal finance startup, and then ultimately settled as a portfolio project exemplary of my current development skills across the full stack, from infrastructure to frontend. I enjoyed working through new problems and getting to work on an application targeted at the FinTech space, as well as becoming very comfortable in new parts of the development process, namely application architecture and CI/CD pipelines. The application now consists of 3 repos, all of which are completely open-source:
- [Finnance App](https://github.com/charlesoller/finnance-app)
- [Finnance API](https://github.com/charlesoller/finnance-api)
- [Finnance Agent Microservice](https://github.com/charlesoller/finnance-agent-microservice)

### Finnance App
The Finnance App repository consists of a Next.js App Router project deployed with AWS Amplify for authentication, Mantine as a CSS library, Zustand as a global store, and TanStack Query to manage external data/caching. Coming into the project, this is certainly the area that I had the greatest experience with. I enjoyed working through variations of designs and creating a UI which displayed rather complex data clearly to an audience that may not have too much background in personal finance before. This repository was set up with GitHub Actions to automate deployment, as well as pre-commit hooks to enforce formatting with ESLint and Prettier. 

### Finnance API
The Finnance API went through multiple iterations throughout the development of Finnance, and is likely the repository where I would change the most if I were to develop it from scratch again. In deployment, the Finnance is hosted on an AWS Lambda Function accessed via API Gateway, protected with Cognito as an Authorizer. 

My original choice to develop this in Python was due to first party support from Stripe and OpenAI APIs, as well as extensive documentation in using Python in a serverless context. Originally, no additional framework was used, and all requests were routed in a dedicated service that extracted the path/request from the request to the lambda handler. I ultimately chose to undergo a fairly significant rewrite to deploy it as a containerized FastAPI application for a few reasons. The first is due to the ease of local development - mocking an API Gateway and Lambda Function locally via the AWS SAM CLI tools was certainly possible, however it wasn't optimal for speed of development. FastAPI offers very easy to setup local development with much faster automatic restart abilities when changes are made. The second, and more important, is portability. By porting this to a containerized FastAPI application (that currently uses Mangum as a handler for the lambda context), this would be very easy to deploy in any context - whether it be on a server or serverless.

I also would likely move from Stripe to a platform like Plaid or an alternative if I were to move this to a production application. I found the data provided by Stripe to be problematic at times, and it only provides 6 months of historical transaction data (compared to alternatives offering 2 years). The costs involved with the Stripe API are a major reason this never moved to a full production application.

Like the Finannce Agent Microservice, this project follows a module structure, consisting of services and handlers. This kept the code very organized and kept any code repetition to the minimum. This repository was also set up with pre-commit hooks and a GitHub action to deploy on push.

### Finnance Agent Microservice
The Finnance Agent Microservice was originally part of the Finnance API, but was refactored out of it due to some key differences in how I wanted responses to be handled. First, all responses are streamed back from this microservice with the EventSource API, compared to the standard responses of the Finnance API. Also, timeout lengths had to be longer due to the agentic tool processing. Though I wanted to keep speed at a maximum (this is the reason for the choice of the completions API, which was then ported to the responses API upon release by OpenAI, over the very slow assistants API), sometimes responses could validly take upwards of 15-30s. I felt that, if deployed to production, the agent functionality should also be independly scalable of general API usage as well, which further supported this microservice.

Like the general API, this also uses a containerized FastAPI service, however its deployed to an EC2 instance via Elastic Beanstalk instead of a lambda. This architecture more readily supports streamed responses as compared to Lambdas and I ultimately feel that this architecture made alot of sense for the purpose of this microservice.

### Testing the Application
Finnance is still available at the live link on top of this README. You're welcome to make a new account or use the provided demo login button. All Stripe integrations will now use the demo institutions rather than real institutions as a cost saving measure. Session history is shared across all users for the sake of demonstrations purposes, so that you can see how you can interact with Finn, and get a little insight into development from the many testing sessions you'll see there.

### Technologies Used
- Typescript
- Python
- Next.js App Router
- FastAPI
- Zustand
- Mantine
- TanStack Query
- EventSource API (for streaming responses)
- Stripe API
- OpenAI Completions API & Responses API
- OpenAI Structured Responses and Tool Calling
- AWS Lambda Functions
- AWS API Gateway
- AWS EC2
- AWS Elastic Beanstalk
- AWS Amplify
- AWS Cognito
- AWS Route 53
- AWS DynamoDB

To run:
```
fastapi dev app/main.py --port 3002
```

Linting: 
- Uses pylint, flake8, black, isort, and mypy
- To run:
```bash
  isort app/
  black app/
  pylint app/
  flake8 app/
  mypy app/
```
- I recommend installing the VSCode extension for each of these to get inline linting
