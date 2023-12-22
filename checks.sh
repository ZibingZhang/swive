DIRS="accounts common registration swive"
python -m isort $DIRS
python -m black $DIRS
