python3 $PWD/../app/main.py
# server warmup
ab -n 1000 -c 25 http://10.77.15.146/search/iphone > /dev/null
ab -n 1000 -c 25 http://10.77.15.146/search/iphone > /dev/null
ab -n 1000 -c 25 http://10.77.15.146/search/iphone > /dev/null
# start testing
ab -n 1000 -c 25 http://10.77.15.146/search/iphone
