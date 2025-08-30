# Barsic Bot

[![Python 3.11](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![aiogram](https://img.shields.io/badge/aiogram-3.4.1-green.svg)](https://aiogram.dev/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)
[![Redis](https://img.shields.io/badge/redis-5.0+-red.svg)](https://redis.io/)
[![CodeQL](https://github.com/sendhello/barsic-bot/actions/workflows/codeql.yml/badge.svg)](https://github.com/sendhello/barsic-bot/actions/workflows/codeql.yml)

A comprehensive Telegram bot service for interacting with the Barsic API platform. Built with modern async Python using aiogram framework, featuring role-based access control, dialog management, and Redis-based state persistence.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Bot Commands](#bot-commands)
- [Development](#development)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)

## Features

- 🤖 **Telegram Bot Interface**: Modern aiogram 3.x based bot with dialog management
- 🔐 **Role-Based Access**: Admin and user role separation with permission filtering
- 📊 **Report Management**: Comprehensive reporting system for users
- ⚙️ **Service Distribution**: Admin-only service distribution and management
- 💾 **Redis Integration**: Persistent state management and caching
- 🛡️ **User Blocking**: Middleware for blocking unauthorized users
- 📱 **Private Chat Only**: Secure private chat interactions
- 🔄 **Dialog System**: Advanced dialog management with aiogram-dialog
- 🚀 **Async Performance**: Full async/await implementation for optimal performance
- 📈 **Error Handling**: Comprehensive error handling and logging

## Tech Stack

- **Bot Framework**: [aiogram](https://aiogram.dev/) 3.4.1
- **Language**: Python 3.11+
- **Dialog Management**: aiogram-dialog 2.1.0
- **Cache/State**: Redis 5.0+
- **HTTP Client**: httpx 0.27.0
- **Configuration**: Pydantic Settings 2.2.1
- **JSON Processing**: orjson 3.10.3
- **ASGI Server**: Uvicorn 0.29.0
- **Code Quality**: Black, Flake8, isort
- **Containerization**: Docker & Docker Compose

## Architecture

The Barsic Bot acts as an interface layer between users and the Barsic API service, providing role-based access to different functionalities.

```
┌─────────────────┐    ┌─────────────────┐
│   Admin Users   │    │  Regular Users  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────────────────┼──────────────────────┐
                                 │                      │
               ┌─────────────────┴─────────────┐        │
               │      Barsic Bot               │        │
               │  (aiogram + Dialog System)    │        │
               └─────────────┬─────────────────┘        │
                             │                          │
               ┌─────────────┴─────────────┐            │
               │        Redis              │            │
               │    (State & Cache)        │            │
               └───────────────────────────┘            │
                                                        │
                                          ┌─────────────┴─────────────┐
                                          │      Barsic API           │
                                          │   (External Service)      │
                                          └───────────────────────────┘
```

### Bot Flow
- **Authentication**: Role-based access with permission filters
- **State Management**: Redis-based dialog state persistence
- **API Integration**: HTTP client for Barsic API communication
- **Menu System**: Hierarchical menu structure with dialog management

## Prerequisites

- **Python**: 3.11 or higher
- **Docker**: 20.10 or higher (for containerized deployment)
- **Redis**: 5.0 or higher
- **Telegram Bot Token**: Obtained from [@BotFather](https://t.me/botfather)

## Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd barsic-bot
   ```

2. **Set up environment variables**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your configuration
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd barsic-bot
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies with Poetry**
   ```bash
   poetry install --no-root
   ```

4. **Set up configuration**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your bot token and settings
   ```

5. **Start Redis (if not using Docker)**
   ```bash
   redis-server
   ```

6. **Start the bot**
   ```bash
   python main.py
   ```

## Configuration

The bot uses a YAML configuration file. Copy `config.yaml.example` to `config.yaml` and configure:

- **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
- **Redis Connection**: Configure Redis host and port
- **API Endpoints**: Set Barsic API service URLs
- **Admin Users**: Configure admin user permissions

## Usage

### Starting the Bot

Once configured and running, users can interact with the bot via Telegram:

1. **Start**: Send `/start` to begin interaction
2. **Authentication**: Bot will verify user permissions
3. **Menu Navigation**: Use inline keyboards to navigate menus
4. **Role-Based Features**: Access features based on your role (Admin/User)

### User Features
- 📊 **Report Management**: Create and view reports
- ℹ️ **Information Menu**: Access bot information and help

### Admin Features
- ⚙️ **Service Distribution**: Manage service distribution settings
- 👥 **User Management**: Control user access and permissions

## Bot Commands

| Command                   | Description                                        | Available To   |
|---------------------------|----------------------------------------------------|----------------|
| `/start`                  | Initialize bot interaction                         | All Users      |
| **Menu-based navigation** | All other features accessible via inline keyboards | Role-dependent |

## Development

### Code Quality Tools

```bash
# Format code
black --line-length 120 .

# Sort imports
isort .

# Lint code
flake8 .
```

### Running in Development Mode

```bash
# Install development dependencies
poetry install

# Run with auto-reload (manual implementation needed)
python main.py
```

## Project Structure

```
barsic-bot/
├── .github/                 # GitHub Actions workflows
│   └── workflows/           # CI/CD pipeline definitions
├── core/                    # Core application configuration
│   ├── logger.py           # Logging configuration
│   └── settings.py         # Application settings
├── db/                     # Database configuration
│   └── redis_db.py         # Redis connection management
├── filters/                # Custom aiogram filters
│   ├── auth.py            # Permission-based filtering
│   └── chat_type.py       # Chat type filtering
├── gateways/              # External API gateways
│   ├── base.py           # Base gateway class
│   └── client.py         # HTTP client implementation
├── handlers/              # Bot command and callback handlers
│   ├── info_menu.py      # Information menu handler
│   ├── main_menu.py      # Main menu handler
│   ├── report_menu.py    # Report management handler
│   ├── service_distribution_menu.py  # Admin service management
│   └── start.py          # Start command handler
├── keyboards/             # Inline keyboard definitions
├── middlewares/           # Custom middleware
│   ├── blocked_user.py   # User blocking middleware
│   └── chat_action.py    # Chat action middleware
├── repositories/          # Data access layer
├── schemas/              # Pydantic data schemas
├── LICENSE.md            # Apache 2.0 license
├── SECURITY.md           # Security policy and guidelines
├── README.md             # Project documentation
├── pyproject.toml        # Poetry configuration
├── main.py              # Application entry point
├── constants.py         # Application constants
├── callbacks.py         # Callback handlers
├── states.py           # Bot state definitions
└── barsic_bot.sh       # Startup script
```

## Environment Variables

| Variable             | Default  | Description                       |
|----------------------|----------|-----------------------------------|
| `BOT_TELEGRAM_TOKEN` | -        | Telegram bot token from BotFather |
| `DEBUG`              | `False`  | Enable debug mode                 |
| `PROJECT_NAME`       | `Barsic` | Service name                      |
| `REDIS_HOST`         | `redis`  | Redis server hostname             |
| `REDIS_PORT`         | `6379`   | Redis server port                 |
| `API_BASE_URL`       | -        | Barsic API base URL               |

## Deployment

### Docker Production Build

```bash
# Build production image
docker build -t barsic-bot:latest .

# Run with production settings
docker run -d \
  --name barsic-bot \
  --env-file .env.prod \
  barsic-bot:latest
```

### System Requirements

- **Minimum**: 1 CPU, 1GB RAM
- **Recommended**: 1 CPU, 2GB RAM
- **Storage**: 5GB for logs and state data
- **Network**: Access to Telegram API, Redis, and Barsic API service

### Health Monitoring

The bot includes comprehensive logging and error handling:
- Critical errors are logged with full stack traces
- User-facing error messages for better UX
- Redis connection monitoring

## Security

Security is important for the Barsic Bot. We implement several security measures:

### Security Features
- **Role-Based Access Control**: Admin and user role separation
- **Private Chat Only**: Bot only responds to private messages
- **User Blocking**: Middleware for blocking unauthorized users
- **Input Validation**: Comprehensive input validation using Pydantic
- **Secure Token Handling**: Secure management of bot tokens and API keys

### Security Policy

For detailed security information and vulnerability reporting, please see our [Security Policy](SECURITY.md).

**Important**:
- Never commit bot tokens to version control
- Use environment variables for sensitive configuration
- Regularly update dependencies
- Monitor bot usage for suspicious activity

### Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: [bazhenov.in@gmail.com](mailto:bazhenov.in@gmail.com) with the subject `[SECURITY] Barsic Bot Vulnerability Report`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality (if applicable)
5. Run code quality checks (`black .`, `flake8 .`, `isort .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public methods
- Use meaningful commit messages
- Update documentation for significant changes

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

Copyright 2025 Ivan Bazhenov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Authors

- **Ivan Bazhenov** - *Initial work* - [@sendhello](https://github.com/sendhello)
  - Email: bazhenov.in@gmail.com

## Support

For support and questions:

- Create an issue on GitHub
- Contact the maintainer via email
- Review existing issues for similar problems

---

**Built with ❤️ using aiogram and Python 3.11+**
