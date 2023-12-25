DIRS="account common registration swive"
python -m black $DIRS
python -m isort $DIRS
python -m pytest $DIRS
