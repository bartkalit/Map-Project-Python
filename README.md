# Map-Project-Python

## Setup
The first thing to do is to clone the repository:
```sh
$ git clone https://github.com/bartkalit/Map-Project-Python.git
$ cd Map-Project-Python
```

Create a virtual environment to install dependencies in and activate it:
```sh
conda create -n env python=3.9
conda activate env
```

Then update pip and install the dependencies:
```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies fill the .env file with proper credentials:
1. [Google Maps API](https://developers.google.com/maps)
2. [TravelTime API](https://traveltime.com/)
```sh
cd Project
python manage.py migrate
python manage.py runserver
```
