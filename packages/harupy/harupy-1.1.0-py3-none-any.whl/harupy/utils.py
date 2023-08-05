#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys


# PEP 3107 -- Function Annotations
# https://www.python.org/dev/peps/pep-3107/

# PEP 484 -- Type Hints
# https://www.python.org/dev/peps/pep-0484/


class Singleton(object):
	"""
	싱글톤 기본 구현 클래스
	"""
	def __new__(cls, *args, **kwargs):
		it = cls.__dict__.get('__it__')
		if it is not None:
			return it
		cls.__it__ = it = object.__new__(cls)
		it.init(*args, **kwargs)
		return it

	def init(self, *args, **kwargs):
		pass


def approximate_size(size, digit):
	"""
	파일 크기 단위 붙이기
	:type size: int
	:param size: Size of a file
	:type digit: 1024 or 1000
	:param digit: Digit to calculate
	:return: str
	"""

	if size < 0:
		raise ValueError('Number must be non-negative')
	if digit not in (1000, 1024):
		raise ValueError('Digit must be 1024 or 1000')

	SIZE_SUFFIXES = {
		1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
		1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
	}

	for suffix in SIZE_SUFFIXES[digit]:
		size /= digit
		if size < digit:
			return '{0:.1f} {1}'.format(size, suffix)

	raise ValueError('number too large')


