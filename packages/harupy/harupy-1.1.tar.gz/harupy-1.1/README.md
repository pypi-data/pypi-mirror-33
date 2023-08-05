# harupy

## 개요

harupy은 파이썬에서 자주 쓰는 기능들을 유틸리티 성격으로 만들어둔 라이브러리입니다.

파이썬으로 개발시 한글 처리를 유연하게 할 수 있도록 한 모듈이 주요 기능이지만,

한글 처리 외에도 개발 실무에서 실제로 필요한 기능들을 쉽게 가져다 쓸 수 있도록 구현해 두었습니다.


## 설치

pip를 통해서 설치합니다.
```
pip install harupy
```


## 사용법

### 문자열

String 클래스로 초기화 하며, josa 메소드를 통해 적절하게 변환된 조사를 붙일 수 있습니다.

```python
>>> from harulib.text import String
>>>
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
>>> String(12000).to_hangul() + '봉'
'만이천봉'
>>> String(12000).to_hangul(read_one=True) + '봉'
'일만이천봉'
```



## Feedback

버그 제보, 개선 요청은 Issues에 올려주시거나, sookim@outlook.jp 로 연락주시면 감사하겠습니다.

풀 리퀘스트는 언제나 환영합니다!

## License

Apache License, Version 2.0

