# finnance-agent-microservice
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