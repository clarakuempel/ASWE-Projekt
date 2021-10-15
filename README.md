# ASWE-Projekt

## setup

Python 3.8 (anything 3.5+ should work) `python -V`

1. create virtual environment `python -m venv venv`
2. activate venv `./venv/Scripts/activate` or `source venv/bin/activate`
3. install requirements `pip install -r requirements.txt`
4. (optional) if you want flake8 (style checker) and pre-commit `pip install flake8 pre-commit`
5. (optional) install pre-commit hook (checks flake8 before commit) `pre-commit install`
6. (optional) run flake and test pre-commit hook `flake8` and `pre-commit run --all-files`