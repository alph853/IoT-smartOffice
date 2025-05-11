src/
├── config/                     # Configuration management
│   ├── config.json            # JSON configuration file
│   └── config.py              # Python configuration module
│
├── domain/                     # Core business logic and domain models
│   ├── events/                # Domain events definitions
│   ├── models/                # Domain models and entities
│   └── repo/                  # Repository interfaces and implementations
│
├── infra/                      # Infrastructure components
│   ├── event_bus/             # Event bus implementation
│   ├── mqtt/                  # MQTT client and related functionality
│   └── scheduler/             # Task scheduling infrastructure
│
├── services/                   # Application services
│   ├── auto_dispatcher.py     # Automatic dispatching service
│   ├── gateway.py             # Gateway service
│   ├── registration.py        # Device registration service
│   ├── scheduler.py           # Scheduling service
│   └── telemetry.py           # Telemetry data handling service
│
├── __init__.py                # Package initialization
└── main.py                    # Application entry point