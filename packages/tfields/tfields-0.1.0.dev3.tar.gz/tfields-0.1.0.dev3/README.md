# Installation
From user side, we recommend the installation via pypi: 
```bash
pip install tfields
```

# Testing:
In the tfields directory, run
```bash
python tfields test
```

# Developers only:
Clone this project with git
To set up the shared git hooks, run
```bash
make init
```

To check the coverage, we prefere the 'coverage' tool
Use it in the tfields directory like so:
```bash
coverage run tfields test
```