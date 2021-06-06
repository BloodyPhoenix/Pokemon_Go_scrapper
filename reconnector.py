# -*- coding: utf-8 -*-

import time


def reconnector(func):
    def decorated_func(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            for _ in range(10):
                time.sleep(5)
                result = func(*args, **kwargs)
                if result:
                    break
        if not result:
            print("Ошибка подключения")
            raise ValueError("Не удалось получить данные")
        return result
    return decorated_func
