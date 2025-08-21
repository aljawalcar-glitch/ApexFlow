# Contributing to ApexFlow

Thank you for your interest in contributing to ApexFlow! This document provides guidelines and information for contributors.

## 🌟 Ways to Contribute

### 🐛 Bug Reports
- Search existing issues before creating new ones
- Use the bug report template
- Include system information and reproduction steps
- Attach sample files when relevant

### 💡 Feature Requests
- Check if the feature already exists or is planned
- Describe the use case and expected behavior
- Consider implementation complexity and maintenance

### 🔧 Code Contributions
- Fork the repository
- Create a feature branch
- Follow coding standards
- Write tests when applicable
- Submit a pull request

### 📖 Documentation
- Improve existing documentation
- Add examples and tutorials
- Translate documentation to other languages
- Fix typos and grammar

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Code editor (VS Code recommended)

### Setup Steps
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/ApexFlow.git
   cd ApexFlow
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```
4. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   ```
5. Run the application to verify setup:
   ```bash
   python main.py
   ```

## 📝 Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions small and focused
- Use type hints where appropriate


### Code Organization
- Place business logic in `modules/`
- Place UI components in `ui/`
- Use the existing architecture patterns
- Keep imports organized and minimal

### Example Code Style
```python
def merge_pdf_files(file_paths: List[str], output_path: str) -> bool:
    """
    Merges multiple PDF files into a single file.
    
    Args:
        file_paths: A list of paths to the PDF files to merge.
        output_path: The path for the output file.
        
    Returns:
        True if the operation was successful, False otherwise.
    """
    try:
        # Implementation here
        return True
    except Exception as e:
        logger.error(f"Error merging files: {e}")
        return False
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_merge.py

# Run with coverage
python -m pytest --cov=modules
```

### Writing Tests
- Write tests for new features
- Test edge cases and error conditions
- Use descriptive test names
- Mock external dependencies

## 📋 Pull Request Process

### Before Submitting
1. Ensure your code follows the style guidelines
2. Run tests and ensure they pass
3. Update documentation if needed
4. Test your changes thoroughly

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes
```

### Review Process
1. Automated checks must pass
2. Code review by maintainers
3. Address feedback and make changes
4. Final approval and merge

## 🌍 Internationalization

### Adding Translations
1. Add new keys to `data/translations.json`.
2. Provide translations for all supported languages.
3. Use the translation system: `tr("key_name")`.
4. Test with all supported languages.

### Translation Guidelines
- Keep translations concise but clear.
- Maintain consistent terminology.
- Consider cultural context.
- Test UI layout with different text lengths.

## 🐛 Issue Guidelines

### Bug Reports Should Include
- **Environment:** OS, Python version, ApexFlow version
- **Steps to Reproduce:** Clear, numbered steps
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Screenshots:** If applicable
- **Sample Files:** If the bug involves specific PDFs

### Feature Requests Should Include
- **Problem Statement:** What problem does this solve?
- **Proposed Solution:** How should it work?
- **Alternatives:** Other ways to solve the problem
- **Additional Context:** Any other relevant information

## 📞 Getting Help

### Communication Channels
- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Email:** support@apexflow.com for private matters

### Response Times
- Bug reports: 1-3 days
- Feature requests: 1-7 days
- Pull requests: 1-5 days

## 📄 License

By contributing to ApexFlow, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributors page

---

Thank you for contributing to ApexFlow! 🚀
