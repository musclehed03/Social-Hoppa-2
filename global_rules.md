# Global Rules for Python/Flask and PostgreSQL Applications

This document outlines the strict constraints and development practices to be followed for Python/Flask and PostgreSQL applications.

## Strict Constraints

1.  **SQLAlchemy for Database Interactions:**
    *   Always use SQLAlchemy for all database interactions.
    *   Do not use raw SQL queries unless absolutely necessary for performance optimization, and only after approval.
    *   Use the Flask-SQLAlchemy extension for integration with Flask.

2.  **No Hardcoded API Keys:**
    *   Never hardcode API keys, secrets, or sensitive credentials directly in the source code.
    *   All sensitive information must be managed through secure configuration management.

3.  **Use Environment Variables:**
    *   Always use environment variables for configuration, including database connection strings, API keys, and environment-specific settings.
    *   Use a `.env` file for local development (ensure it is added to `.gitignore`).
    *   Use `os.environ.get()` or a library like `python-dotenv` to load these variables.

4.  **Explain Approach Before Writing Code:**
    *   Always provide a clear explanation of the approach, architecture, and logic before writing any code.
    *   This ensures alignment on the solution and facilitates better code reviews.

## Development Best Practices

*   **Follow PEP 8:** Adhere to the official Python style guide for clean and readable code.
*   **Modular Architecture:** Organize the application into blueprints or modules for better maintainability.
*   **Error Handling:** Implement robust error handling and logging to facilitate debugging and monitoring.
*   **Testing:** Write unit and integration tests to ensure code quality and prevent regressions.
