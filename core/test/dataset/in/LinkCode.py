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

        val = "The result of %s is %s" % (func(), eval(func()))

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
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


@another_function
def a_function():
    """Обычная `функция`"""
    return "1+1"


__name__ = '__main__'

if __name__ == "__main__":
    print(a_function.__name__)  # a_function
    print(a_function.__doc__)  # Обычная функция
