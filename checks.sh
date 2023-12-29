DIRS="account common registration root swive"
python -m black $DIRS
python -m isort $DIRS
python -m pytest $DIRS
