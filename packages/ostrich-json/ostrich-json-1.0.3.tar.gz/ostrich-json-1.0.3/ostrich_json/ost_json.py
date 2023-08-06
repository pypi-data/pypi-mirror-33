import json
import time


def dump(fp_data):
    return json.dumps(fp_data)


def dumps(data, logger=None, ensure_ascii=True):
    if isinstance(data, dict):
        pass
    else:
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError, ValueError) as E:
            pass
        if isinstance(data, dict):
            pass
        else:
            if logger:
                logger.error('非字典类型数据dump成了json', extra=data)
    return json.dumps(data, ensure_ascii=ensure_ascii)


def load(fp_data):
    return json.load(fp_data)


def loads(data, logger=None):
    try:
        data = json.loads(data)
    except (json.JSONDecodeError, json.decoder.JSONDecodeError, TypeError, ValueError) as E:
        data = json.loads(json.dumps({'no_json': str(data), 'catch_time': int(time.time())}))
        if logger:
            logger.error('force to json', extra=data)
    return data


if __name__ == '__main__':
    # print(loads(loads(dumps(dumps('12345{{}}//', '')))))
    print(loads(dumps(dumps({1: 2, 3: 4}))))
