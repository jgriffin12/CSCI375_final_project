# Install all Python dependencies from requirements.txt
install:
	pip install -r requirements.txt

# Run the Flask application locally
run:
	python -m app.main

# Run all tests
test:
	pytest

# Run static type checking on the app package
typecheck:
	mypy apps