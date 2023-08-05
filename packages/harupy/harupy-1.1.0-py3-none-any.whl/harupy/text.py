#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018 Soo Kim.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from functools import wraps


class String(str):
	"""
	기본 내장객체 str를 확장하여 한글 처리 로직이 추가된 문자열 오브젝트
	"""

	def __new__(cls, object):
		return str.__new__(cls, object)

	def __add__(self, other):
		return String(super(String, self).__add__(other))

	def __radd__(self, other):
		return String(other.__add__(self))

	def __mul__(self, other):
		return String(super(String, self).__mul__(other))

	def __rmul__(self, other):
		return String(super(String, self).__rmul__(other))

	def __getitem__(self, item):
		return String(super(String, self).__getitem__(item))

	def __iter__(self):
		for s in self.__str__():
			yield String(s)

	def __getattribute__(self, item):
		if 44031 < ord(item[0]) < 55204:
			if String(item).hangul_rate() == 100:
				return self.josa(item)
		rtn = super(String, self).__getattribute__(item)
		if rtn.__class__.__name__ in ('method', 'builtin_function_or_method'):
			return self.string_object_decorator(rtn)
		else:
			return rtn

	@staticmethod
	def string_object_decorator(func):
		"""
		String 객체의 각 메소드에서 리턴 데이터를 다시 String 객체로 변환하는 데코레이터
		"""
		@wraps(func)
		def wrapper(*args, **kwargs):
			result = func(*args, **kwargs)
			if type(result) is str:
				return String(result)
			elif type(result) is tuple:
				return tuple([String(s) for s in result])
			elif type(result) is list:
				return [String(s) for s in result]
			else:
				return result

		return wrapper

	def to_hangul(self, read_one=False):
		if not super(String, self).isdecimal():
			raise ValueError('Value must be integer-like string.')
		return self._read_number(read_one)

	def _read_number(self, read_one):
		number_string = ('', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구')
		number_string_10 = ('', '십', '백', '천')
		number_string_10k = ('', '만', '억', '조', '경', '해', '자', '양', '구', '간', '정', '재', '극')

		number = self

		if number == '0':
			return '영'
		if number == '1':
			return number_string[1]

		def _read_under_10k(under_10k):
			reading_10k = ''
			for i in range(0, len(under_10k)):
				reading_number = number_string[int(under_10k[-i-1])] if under_10k[-i-1] != '1' or i == 0 or read_one else ''
				reading_10k = ((reading_number + number_string_10[i]) if under_10k[-i-1] != '0' else '') + reading_10k
			return reading_10k

		# 4문자씩 나눠 읽기
		i = 0
		reading = ''
		while number:
			if len(number) > 4:
				split = number[-4:]
				number = number[:-4]
			else:
				split = number
				number = ''
			prefix = _read_under_10k(split)
			reading = (prefix if prefix != '일' or not number_string_10k[i] or read_one else '') + number_string_10k[i] + reading
			i += 1
		return reading

	def isdecimal(self):
		"""
		한글로 읽은 숫자까지 결과에 반영
		:return: bool
		"""
		return super(String, self).isdecimal()

	def hangul_rate(self):
		"""
		전체 문자열에서 한글인 문자열의 백분율(%)을 반환
		:return: int
		"""
		total = len(self)
		hangul_count = 0
		for i in range(total):
			code_num = ord(self[i])
			if 44031 < code_num < 55204 or 12592 < code_num < 12644:
				hangul_count += 100
		return int(hangul_count / total)

	def extract_readable(self, only_hangul=False):
		readable = ''
		for s in self:
			code_num = ord(s)
			if 44031 < code_num < 55204:
				readable += s
			elif only_hangul is False and (12592 < code_num < 12623 or 12622 < code_num < 12644 \
					or 96 < code_num < 123 or 64 < code_num < 91 or 47 < code_num < 58):
				readable += s
		return readable

	def get_last_bachim(self):
		"""
		마지막 글자 또는 마지막 글자의 읽는 방법을 기준으로 받침을 반환함
		받침이 없는 경우 빈 문자열('') 반환
		단, 알파벳의 경우
		받침을 알 수 없는 경우 None을 반환
		"""
		readable = self.extract_readable()
		if not readable:
			return None
		code_num = ord(readable[-1])

		if 47 < code_num < 58:
			# 숫자
			return (
				'ㅇ', 'ㄹ', '', 'ㅁ', '', '', 'ㄱ', 'ㄹ', 'ㄹ', ''
			)[code_num - 48]
		elif 64 < code_num < 91:
			# 알파벳 대문자
			return (
				'', '', '', '', '', '', '', '', '', '', '', 'ㄹ', 'ㅁ', 'ㄴ', '', '', '', 'ㄹ',
				'', '', '', '', '', '', '', ''
			)[code_num - 65]
		elif 96 < code_num < 123:
			# 알파벳 소문자
			return (
				'', 'ㅂ', 'ㄱ', '', '', '', 'ㄱ', '', '', '', 'ㄱ', 'ㄹ', 'ㅁ', 'ㄴ', '', 'ㅂ', '', '',
				'', '', '', '', '', '', '', ''
			)[code_num - 97]
		elif 44031 < code_num < 55204:
			# 한글
			return (
				'ㄹㅅ', 'ㄹㅌ', 'ㄹㅍ', 'ㄹㅎ', 'ㅁ', 'ㅂ', 'ㅂㅅ', 'ㅅ', 'ㅅㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ',
				'ㅍ', 'ㅎ', '', 'ㄱ', 'ㄱㄱ', 'ㄱㅅ', 'ㄴ', 'ㄴㅈ', 'ㄴㅎ', 'ㄷ', 'ㄹ', 'ㄹㄱ', 'ㄹㅁ', 'ㄹㅂ'
			)[code_num % 28]
		elif 12592 < code_num < 12623:
			# 한글 자음
			return (
				'ㄱ', 'ㄱ', 'ㅅ', 'ㄴ', 'ㅈ', 'ㅎ', 'ㄷ', 'ㄷ', 'ㄹ', 'ㄱ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅌ', 'ㅍ',
				'ㅎ', 'ㅁ', 'ㅂ', 'ㅂ', 'ㅅ', 'ㅅ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
			)[code_num - 12593]
		elif 12622 < code_num < 12644:
			# 한글 모음
			return ''

	def josa(self, josa_str):
		"""
		앞글자의 받침에 따라 변화하는 조사 붙이기
		:param josa_str: 붙일 조사
		:return: 적절한 조사를 붙인 문자열
		"""
		if type(josa_str) not in (str, String):
			raise ValueError('Josa must be string type.')
		if self == '':
			raise ValueError('String value must not be empty.')

		josa_tuple = ('으로', '로', '이', '가', '은', '는', '을', '를', '과', '와', '아', '야')

		if josa_str not in josa_tuple:
			# '이'로 시작하는 모든 조사 및 술어
			# '이랑', '랑', '이여', '여', '이다', '다', '이고', '고', '이며', '며', '이라고', '라고', '이라며', '라며', '이라면', '라면',
			# '이라는', '라는', '이라서', '라서', '이야말로', '야말로' 등등...
			return self + ('', '이')[1 if self.get_last_bachim() else 0] + josa_str.lstrip('이')

		index = (josa_tuple.index(josa_str) // 2) * 2
		bachim = self.get_last_bachim()

		return self + josa_tuple[index + (0 if bachim and (bachim != 'ㄹ' or index) else 1)]

