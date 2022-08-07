Камень в огород `HR`

- Что они спрашивают на собеседование

  ```python [Пузырьковая сортировка]{1,8}
  def bubble_sort(nums):
      # Устанавливаем swapped в True, чтобы цикл запустился хотя бы один раз
      swapped = True
      while swapped:
          swapped = False
          for i in range(len(nums) - 1):
              if nums[i] > nums[i + 1]:
                  # Меняем элементы
                  nums[i], nums[i + 1] = nums[i + 1], nums[i]
                  # Устанавливаем swapped в True для следующей итерации
                  swapped = True

  # Проверяем, что оно работает
  random_list_of_nums = [5, 2, 1, 8, 4]
  bubble_sort(random_list_of_nums)
  print(random_list_of_nums)
  ```

  ```python [Сортировка выборкой]{3,5-8}
  def selection_sort(nums):
      # Значение i соответствует кол-ву отсортированных значений
      for i in range(len(nums)):
          # Исходно считаем наименьшим первый элемент
          lowest_value_index = i
          # Этот цикл перебирает несортированные элементы
          for j in range(i + 1, len(nums)):
              if nums[j] < nums[lowest_value_index]:
                  lowest_value_index = j
          # Самый маленький элемент меняем с первым в списке
          nums[i], nums[lowest_value_index] = nums[lowest_value_index], nums[i]

  # Проверяем, что оно работает
  random_list_of_nums = [12, 8, 3, 20, 11]
  selection_sort(random_list_of_nums)
  print(random_list_of_nums)
  ```

  ```python [Сортировка вставками]{1-5}
  def insertion_sort(nums):
      # Сортировку начинаем со второго элемента, т.к. считается, что первый элемент уже отсортирован
      for i in range(1, len(nums)):
          item_to_insert = nums[i]
          # Сохраняем ссылку на индекс предыдущего элемента
          j = i - 1
          # Элементы отсортированного сегмента перемещаем вперёд, если они больше
          # элемента для вставки
          while j >= 0 and nums[j] > item_to_insert:
              nums[j + 1] = nums[j]
              j -= 1
          # Вставляем элемент
          nums[j + 1] = item_to_insert

  # Проверяем, что оно работает
  random_list_of_nums = [9, 1, 15, 28, 6]
  insertion_sort(random_list_of_nums)
  print(random_list_of_nums)
  ```

  ```python [Пирамидальная сортировка]{5-8}
  def heapify(nums, heap_size, root_index):
      # Индекс наибольшего элемента считаем корневым индексом
      largest = root_index
      left_child = (2 * root_index) + 1
      right_child = (2 * root_index) + 2

      # Если левый потомок корня — допустимый индекс, а элемент больше,
      # чем текущий наибольший, обновляем наибольший элемент
      if left_child < heap_size and nums[left_child] > nums[largest]:
          largest = left_child

      # То же самое для правого потомка корня
      if right_child < heap_size and nums[right_child] > nums[largest]:
          largest = right_child

      # Если наибольший элемент больше не корневой, они меняются местами
      if largest != root_index:
          nums[root_index], nums[largest] = nums[largest], nums[root_index]
          # Heapify the new root element to ensure it's the largest
          heapify(nums, heap_size, largest)

  def heap_sort(nums):
      n = len(nums)

      # Создаём Max Heap из списка
      # Второй аргумент означает остановку алгоритма перед элементом -1, т.е.
      # перед первым элементом списка
      # 3-й аргумент означает повторный проход по списку в обратном направлении,
      # уменьшая счётчик i на 1
      for i in range(n, -1, -1):
          heapify(nums, n, i)

      # Перемещаем корень Max Heap в конец списка
      for i in range(n - 1, 0, -1):
          nums[i], nums[0] = nums[0], nums[i]
          heapify(nums, i, 0)

  # Проверяем, что оно работает
  random_list_of_nums = [35, 12, 43, 8, 51]
  heap_sort(random_list_of_nums)
  print(random_list_of_nums)
  ```

Когда приходишь в их продакшн

- В продакшене

  ```python [Вриант 1]
  random_list_of_nums = sorted([9, 1, 15, 28, 6])
  ```

  ```python [Вариант 2]
  random_list_of_nums = [9, 1, 15, 28, 6].sort()
  ```
