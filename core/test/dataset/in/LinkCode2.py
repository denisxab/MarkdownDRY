# Обычная функция


def a_function():
    """Обычная `функция`"""
    return "1+1"


__name__ = '__main__'

if __name__ == "__main__":
    # ДелаемДела>
    print(a_function.__name__)  # a_function
    # <ДелаемДела
    print(a_function.__doc__)  # Обычная функция
