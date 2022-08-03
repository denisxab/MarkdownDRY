# Обычная функция
from functools import wraps


class NeClass:
    name: str = __file__

    def __call__(self, *args, **kwargs):
        """Доки"""
        return self.name


def another_function(func):
    """
    Функция которая принимает другую функцию
    """

    @wraps(func)  # !!
    def wrapper():
        """
        Оберточная функция
        """
        # Химичим>

        val = "The result of %s iSs %ss" % (func(), eval(func()))




        # <Химичим
        return val

    return wrapper


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+2"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+3"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+4"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+5"


__name__ = '__main__'

if __name__ == "__main__":
    print(a_function.__name__)  # a_function
    print(a_function.__doc__)  # Обычная функция