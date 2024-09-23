# Packages

### **yfinance**
    - 1996년 12월 11일 부터 데이터 존재. 그래서 1980년 1월 4일 코스피 100부터 시작되는 데이터가 존재하지 않음



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
