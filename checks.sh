DIRS="accounts common registration swive"
python -m black $DIRS
python -m isort $DIRS
