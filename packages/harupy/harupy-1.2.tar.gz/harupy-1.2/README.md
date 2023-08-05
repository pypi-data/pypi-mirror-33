# harupy

## Overview

harupy은 파이썬으로 개발시 한글 처리를 유연하게 할 수 있도록 한 모듈이 주요 기능입니다.

한글 처리 외에도 개발 실무에서 실제로 필요한 텍스트 처리 기능들을 이후로도 추가할 계획입니다.


## Install

pip를 통해서 설치합니다.
```
pip install harupy
```


## Usage

### String

한글 처리 관련 문자열 객체는 `String` 입니다. 내장 객체인 `str`의 확장이므로, 기본적으로 `str` 객체와 동일하게 사용 가능합니다.

```python
>>> from harupy.text import String
```

`josa()` 메소드를 통해 적절하게 변환된 조사를 붙일 수 있습니다.

```python
>>> name1 = String('김수안무')
>>> name2 = String('삼천갑자 동방삭')
>>>
>>> name1.josa('이')
'김수안무가'
>>> name2.josa('가')
'삼천갑자 동방삭이'
>>>
>>> title = '신세계'
>>> String(title).josa('이라는') + ' 영화 봤나요?'
'신세계라는 영화 봤나요?'
```

올바른 방법은 아니라고 생각하지만, 사용상의 편의를 위해 속성값으로 조사를 직접 입력하는 것을 허용해두었습니다.

이 방법을 사용하면 한글로 된 속성값을 자동으로 josa 메소드의 결과값으로 표시합니다.

```python
>>> target = String('오솔길')
>>> target.로
'오솔길로'
>>> String('호떡').이나 + ' 먹자'
'호떡이나 먹자'
>>> String('떡볶이').이나 + ' 먹자'
'떡볶이나 먹자'
>>> String('게').나 + ' ' + String('고동').나
'게나 고동이나'
```

숫자를 한글로 읽을 수 있습니다.

```python
>>> price = String(152000)
>>> price.to_hangul()
'십오만이천'
>>> String('37501600').to_hangul()
'삼천칠백오십만천육백'
```

1을 생략하지 않고 읽는 방법도 있습니다.

```python
>>> String(1110000).to_hangul()
'백십일만'
>>> String(1110000).to_hangul(read_one=True)
'일백일십일만'
```

반대로 한글로 읽은 숫자를 정수로 변환하는 `to_number()`도 사용할 수 있습니다.

```python
>>> String('이천십팔').to_number(True)
2018
>>> String('천이백십일억천백만').to_number()
121111000000
```

또한, 내장 str 객체의 `isnumeric()`을 확장하여, 한글로 읽은 숫자에 대해서도 참으로 판단할 수 있습니다.

```python
>>> String('사천오백만').isnumeric()
True
```

## Feedback

버그 제보, 개선 요청은 Issues에 올려주시거나, sookim@outlook.jp 로 연락주시면 감사하겠습니다.

풀 리퀘스트는 언제나 환영합니다!

## License

Apache License, Version 2.0

