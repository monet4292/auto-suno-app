# Project Context

## Purpose
Suno Account Manager v2.0 là một ứng dụng desktop Windows chuyên nghiệp được thiết kế để quản lý tài khoản Suno.com và tự động hóa việc tạo nhạc hàng loạt. Ứng dụng cung cấp các tính năng chính:
- Quản lý đa tài khoản Suno với session persistence 24h
- Tự động tạo hàng loạt bài hát từ XML prompts với hệ thống queue thông minh
- Batch download với metadata ID3 tags đầy đủ
- Hệ thống anti-CAPTCHA thông minh để giảm tỷ lệ bị chặn
- Theo dõi lịch sử tạo bài và download với khả năng export CSV

## Tech Stack
- **Language**: Python 3.10+
- **GUI Framework**: CustomTkinter 5.2.0+ (Modern dark theme UI)
- **Browser Automation**: Selenium 4.15.0+ với Stealth WebDriver
- **HTTP Client**: Requests 2.31.0+
- **Audio Metadata**: Mutagen 1.47.0+ (ID3 tags)
- **WebDriver Management**: webdriver-manager 4.0.1+
- **Terminal Colors**: Colorama 0.4.6+

## Project Conventions

### Code Style
- **Language**: Python 3.10+ với PEP 8 compliance
- **Naming Conventions**:
  - Classes: PascalCase (AccountManager, MainWindow)
  - Functions/Variables: snake_case (create_account, account_name)
  - Constants: UPPER_SNAKE_CASE (MAX_RETRY_ATTEMPTS)
  - Files: lowercase_with_underscores (account_manager.py)
- **Type Hints**: Exhaustive type hints cho public methods
- **Docstrings**: Google style với module-level docstrings
- **Comments**: Tiếng Việt (vi-VN)
- **Logging**: Sử dụng logger thay vì print()

### Architecture Patterns
- **Clean Architecture** với 4 layers:
  1. Presentation Layer (src/ui/) - UI components
  2. Application Layer (src/core/) - Business logic
  3. Domain Layer (src/models/) - Data models
  4. Infrastructure Layer (src/utils/) - Utilities
- **Dependency Rules**: UI → Core → Models → Utils (không import ngược)
- **Design Patterns**:
  - Dependency Injection: Managers injected vào UI panels
  - Repository Pattern: JSON files cho persistent storage
  - Observer Pattern: Progress callbacks cho UI updates
  - Singleton: Logger instance
  - Factory: StealthDriver creation
  - State Machine: Queue status transitions

### Testing Strategy
- **Framework**: pytest
- **Test Structure**:
  - Unit tests cho individual components
  - Integration tests cho workflows
  - Stress tests cho queue system
- **Test Files Location**: tests/
- **Mocking**: Mock external dependencies (ChromeDriver, API calls)
- **Coverage Priority**: Account persistence, Session token retrieval, Queue workflows, Download orchestration

### Git Workflow
- **Branching Strategy**: 
  - main/master cho production
  - feature/* cho features mới
  - fix/* cho bug fixes
- **Commit Convention**:
  ```
  feat(scope): description
  fix(scope): description
  docs(scope): description
  refactor(scope): description
  test(scope): description
  ```
- **PR Requirements**: Motivation, testing evidence, documentation updates, screenshots/logs

## Domain Context
- **Suno.com**: AI music generation platform sử dụng Clerk.com authentication
- **Session Management**: JWT tokens trong cookies + localStorage metadata
- **Chrome Profile Isolation**: Mỗi account có profile riêng biệt để preserve session
- **Anti-CAPTCHA**: Stealth driver với User-Agent rotation và human-like delays
- **Queue System**: Multi-queue management với state persistence và resume capability

## Important Constraints
- **Platform**: Windows 10/11 (64-bit) only
- **Chrome**: Required browser cho automation
- **Session Lifetime**: 24h maximum cho JWT tokens
- **Rate Limiting**: Suno API limits (30 req/min cho /feed/v2, 60 req/min cho /clips/profile)
- **CAPTCHA Risk**: Tỷ lệ CAPTCHA <5% với manual submit, tăng lên với auto-submit
- **Security**: Không commit Chrome profiles, sensitive data files

## External Dependencies
- **Suno.com API**: Reverse engineered endpoints cho song creation và download
- **Clerk.com**: Authentication system với JWT tokens
- **Chrome WebDriver**: Browser automation với stealth capabilities
- **File System**: Profile isolation, download organization
- **JSON Storage**: Persistent data trong data/ directory

## Key Directories Structure
```
F:\auto-suno-app\
├── app.py                          # Entry point - CustomTkinter GUI
├── config/
│   ├── settings.py                 # Centralized configuration
│   └── style_config.py             # UI styling configuration
├── src/
│   ├── ui/                         # Presentation Layer
│   ├── core/                       # Application Layer
│   ├── models/                     # Domain Layer
│   └── utils/                      # Infrastructure Layer
├── data/                           # Runtime data (gitignored)
├── profiles/                       # Chrome profiles (gitignored)
├── downloads/                      # Downloaded songs (gitignored)
├── logs/                           # Application logs (gitignored)
└── tests/                          # Test suite
```

## Configuration Management
- **Central Settings**: config/settings.py chứa paths, API URLs, app settings
- **Style Configuration**: config/style_config.py cho UI styling
- **Data Persistence**: JSON files trong data/ directory
- **Chrome Profiles**: profiles/ directory cho browser state isolation

## Security Considerations
- **Session Tokens**: Refresh mỗi 24h maximum
- **Chrome Profiles**: NEVER commit đến git
- **Sensitive Data**: Tất cả JSON files trong data/ gitignored
- **Personal Accounts**: Chỉ sử dụng tài khoản của riêng bạn
- **Anti-Detection**: Stealth driver với human-like behaviors
