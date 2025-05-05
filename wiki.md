# Project Summary
The project is a modular Python application named "Shamann," designed to enhance penetration testing capabilities. It integrates various functionalities, focusing on security assessments, AI-related tasks, and robust database operations. The project aims to provide developers with tools for effective pentesting while ensuring maintainability and scalability.

# Project Module Description
- **ai_oracle**: Contains functionalities related to artificial intelligence.
- **core**: Central business logic, including logging configurations.
- **db**: Manages database operations.
- **logs**: Handles application logging.
- **modules**: Hosts modular components, including the `whois_guardian` and a new `recon` module for pentesting.
- **output**: Directory for output files and results.
- **config**: Manages application configuration settings.
- **tests**: Framework for unit testing.
- **shamann.py**: Main entry point for the application.

# Directory Tree
```
.
├── ai_oracle                      # AI-related functionalities
├── core                           # Core functionality and business logic
│   ├── __init__.py
│   ├── logger.py                  # Logging configuration
│   └── logging_config.py          # Advanced logging structure for pentesting
├── db                             # Database related operations
├── logs                           # Application logging
├── modules                        # Modular components
│   ├── __init__.py
│   ├── whois_guardian.py         # Main module functionality
│   └── recon                      # New reconnaissance module for pentesting
│       ├── __init__.py
│       ├── port_scanner.py       # Port scanning functionality
│       ├── dns_enum.py           # DNS enumeration functionality
│       └── http_recon.py         # HTTP reconnaissance functionality
├── output                         # Output files and results
├── config                         # Configuration management
│   ├── __init__.py
│   └── settings.py                # Application settings
├── tests                          # Testing framework
│   ├── __init__.py
│   └── test_whois_guardian.py    # Unit tests for whois_guardian
├── requirements.txt               # Project dependencies
├── shamann.py                     # Main application entry point
├── README.md                      # Project documentation
└── CONFIGURACAO.md                # Detailed instructions in Portuguese for setup
```

# File Description Inventory
- **README.md**: Documentation for the project.
- **CONFIGURACAO.md**: Instructions in Portuguese for setting up the environment.
- **analysis_report.json**: Report on project structure and recommendations.
- **config/**: Directory for configuration files.
- **core/**: Core logic and functionalities, including logging configuration.
- **modules/**: Contains modular components, including the new reconnaissance module.
- **requirements.txt**: Lists project dependencies, including new security libraries.
- **shamann.py**: Main script to run the application.
- **tests/**: Contains test cases for the application.

# Technology Stack
- **Programming Language**: Python 3.12 (via pyenv)
- **IDE**: Kate
- **Shell**: zsh
- **Testing Framework**: pytest
- **Dependency Management**: requirements.txt

# Usage
1. **Navigate to the project directory**:
   ```bash
   cd /data/chats/fwmsvd/workspace
   ```

2. **Create the virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Upgrade pip**:
   ```bash
   pip install --upgrade pip
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify installation**:
   ```bash
   python --version  # Should show Python 3.12.x
   pip list          # Lists installed packages
   ```

7. **Run the main application**:
   ```bash
   python shamann.py
   ```

8. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

9. **Deactivate the virtual environment when done**:
   ```bash
   deactivate
   ```
