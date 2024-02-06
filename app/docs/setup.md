# 🚀 Setting up Docflow Locally

Just a 3-step process to get Docflow up and running on your local machine! 🌐

### 1️⃣ Clone the repository

```bash
git clone https://www.github.com/jiisanda/docflow.git
```

### 2️⃣ Configure Your Environment

Start by creating your environment file using the provided [.env.template](https://github.com/jiisanda/docflow/blob/master/.env.template).
This file contains all the necessary environment variables for Docflow. Save it inside the app/ directory.

#### PostgreSQL Setup

Set up your PostgreSQL environment variables:

- `DATABASE_HOSTNAME`: By default, set to `postgres`.
- `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_PORT`:  Enter your PostgreSQL username, password, and port 
(default is `5432`).
- `POSTGRES_DB` and `POSTGRES_DB_TESTS`: Specify your database names (`POSTGRES_DB_TESTS` can be left blank).

#### AWS Setup
For AWS credentials (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`), follow these steps:

>1. Sign in to the [AWS Management Console]() using your AWS account's root user credentials.
>2. Navigate to Security Credentials and create an access key.
>3. Copy the access key ID and secret key securely.
>4. For S3 bucket setup, refer to creating a [bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html).
>
> Source: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user_manage_add-key.html

#### User Environment

Keep `ACCESS_TOKEN_EXPIRE_MIN` and `REFRESH_TOKEN_EXPIRE_MIN` as default. Update the `ALGORITHM` of your choice (e.g., `HS256` or `RS256`).

Generate `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY` using Python:
```bash
docflow$ python
>> import secrets
>> secrets.token_urlsafe(32)
'some-random-secret-of-length-32'
>> secret.token_hex(32)
'some-random-secret-of-length-32'
```
#### Email Service

This section explains how to set up the email service using Gmail. Configure the following variables:
```.ignorelang
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL=Your email address used to create the app
APP_PASSWORD=Generate an app password from your Google Account
```

Before starting, ensure you have enabled "Two-Factor Authentication" and "Less secure app access" for your Gmail account.

>For a deeper understanding of environment variables in Python, check out this article: 
>[@dev.to/jiisanda](https://dev.to/jiisanda/how-does-python-dotenv-simplify-configuration-management-3ne6)


### 3️⃣ Run with Docker-Compose

Ensure Docker is installed, then run:

```commandline
docker-compose up --build
```

That's it! Docflow is now running on localhost:8000. 

If you face any issues, contact me I will help you set up or start an EC2 instance for testing docflow.

## ⏭️ Next Step

To test it, use Postman following the steps in 
[postman.md](features/postman.md).
***