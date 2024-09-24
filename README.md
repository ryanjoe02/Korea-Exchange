# Packages

### **yfinance**
  - 1996년 12월 11일 부터 데이터 존재. 그래서 1980년 1월 4일 코스피 100부터 시작되는 데이터가 존재하지 않음

  - yfiance doesn't handle filtering based on companrsions (greater_than, less_than etc)

    Solved: Fetching data with yfinance -> Manual Comparison logic -> implementation
    


### **polyon.io**
  - 회사의 이름만 가지고 ticker를 조회하기 위해서 사용

# Implemented Features

### **1. Custom Login**

- During login, users can obtain a token using either a 

  **username or email** along with a **password**.
  
  Originally, it was only possible to log in with a **username and password**, but this has been customized.

- Test User:
  - Username: test1
  - Email: test1@gmail.com
  - Password: user@123

- Result 

  Bash : curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "test1", "password": "user@123"}'

  Bash : curl -X POST http://127.0.0.1:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "test1@gmail.com", "password": "user@123"}'

  Token : {"token":"98b5d7faafa0a41ff2f170f5eb1b8fba60ee8afe"}%

### **2. NLP (en)**

- NLP to interpret user queries in English



### 수정해야 할 사항들 ###

1. 상장된 회사들이 너무 많다. 예를들어 사용자가 Apple 을 치면 apple hospitality (APLE) 그리고 우리가 흔히 아는 AAPL 등이 나오는데

이 부분은 사용자가 먼저 타이핑 하고 2차로 어느회사를 지칭하는지 사용자가 직접 선택하도록 block을 만들어야겠다.

2. 무료 API 를 이용해서 모든 회사들의 정보를 검색할 순 없어서 한계가 있다. 최대한 여려 APIs 를 사용하면서 어떤 것이 좋은지 사용해봐야겠다.
