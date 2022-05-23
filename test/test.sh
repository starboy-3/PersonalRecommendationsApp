pip install -r $PWD/../app/requirements.txt
python3 $PWD/../app/main.py
ab -n 1000 -c 25 http://192.168.211.84:8080/search/iphone
