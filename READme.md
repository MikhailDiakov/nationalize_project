# 🚀 Notionalize API

## 📖 About the project

This project is a service that predicts a person’s likely country of origin based on their name.

It uses two public APIs:

Nationalize.io — predicts nationality by name
REST Countries — provides detailed country information

The result is a simple but useful tool for analyzing names and related data.

## 📌 Startup

To set up and run the project, use the following commands:

```bash
git clone <repository URL>
cd <project directory>
cp .env.example .env
docker-compose up -d
```

Access the API documentation at: [http://localhost/api/docs/#/](http://localhost/api/docs/#/)


## 📦 What's inside the .env.example file?

The .env.example file contains all essential environment variables with clear explanations of what each setting does — from Django’s secret key and debug mode, to database connection details like host, port, user, and password.

Make sure to review it and set your own values before running the project!

## Testing

- **Pytest**:
  ```
  docker-compose --profile test up
  ```
  or in the docker container.
---
