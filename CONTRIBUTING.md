# Contributing to AlphaLearn

We love your input! We want to make contributing to AlphaLearn as easy and transparent as possible.

## Development Process

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Make sure tests pass
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update version numbers in any examples files and the README.md
3. The PR will be merged once you have the sign-off of at least one maintainer

## Development Setup

### Backend

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

## Code Style

- Follow existing code patterns
- Use TypeScript for frontend
- Use type hints for Python backend
- Write descriptive commit messages

## Bug Reports

When filing an issue, make sure to answer these questions:

1. What version are you using?
2. What operating system and browser are you using?
3. What did you do?
4. What did you expect to see?
5. What did you see instead?

## Feature Requests

We welcome feature requests! Please provide:

1. A clear description of the feature
2. Why you think it would be useful
3. Any relevant examples or mockups

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
