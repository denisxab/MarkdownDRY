import os
import re
from pprint import pprint


def read_env_file_and_set_from_venv(file_name: str):
	"""Чтение переменных окружения из указанного файла, и добавление их в ПО `python`"""
	with open(file_name, 'r', encoding='utf-8') as _file:
		res = {}
		for line in _file:
			tmp = re.sub(r'^#[\s\w\d\W\t]*|[\t\s]', '', line)
			if tmp:
				k, v = tmp.split('=', 1)
				# Если значение заключено в двойные кавычки, то нужно эти кавычки убрать
				if v.startswith('"') and v.endswith('"'):
					v = v[1:-1]

				res[k] = v
	os.environ.update(res)
	pprint(res)
