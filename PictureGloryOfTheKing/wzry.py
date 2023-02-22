import requests
import json


def main():
    resp = requests.get('https://apis.tianapi.com/scwd/index?key=e645d44c949295268bf08b9b151f73fe')
    data_model = resp.json()
    for key, values in data_model['result'].items():
        print(values)


if __name__ == '__main__':
    main()