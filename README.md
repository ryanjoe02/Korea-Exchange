# Packages

### **yfinance**
  - 1996년 12월 11일 부터 데이터 존재. 그래서 1980년 1월 4일 코스피 100부터 시작되는 데이터가 존재하지 않음

  - yfiance doesn't handle filtering based on companrsions (greater_than, less_than etc)

    Solved: Fetching data with yfinance -> Manual Comparison logic -> implementation
    


### **polyon.io**
- 회사의 이름만 가지고 ticker를 조회하기 위해서 사용

- 하지만 무료 버전은 시간 당 몇번의 요청밖에 쓸 수 없어서 yfinance를 그대로 사용하기로 결정 

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

### **3. User**

- /auth/user/로 API 요쳥을 보내서 유저를 생성하려면 4가지가 필요하다

  ```
  {
    "email": "",
    "username": "",
    "password": "",
    "re_password": ""
  }
  ```

### **4. Search**

- `/api/stock-query`

  Requeset :
  ```
    {"query": "When did Apple stock exceed 120 dollars?"}
  ```

  Response :

    ETFs are being retrieved, but for exchanges that are not registered, 'N/A' is displayed

    ![Alt text](/pics/stock-query.png)

- `/api/stock-data-search/`

  Request :
  ```
    {
      "ticker": "AAPL",
      "price": 120,
      "comparison_type": "greater_than_equal"
    }
  ```
  
  Response :

  ![Alt text](/pics/stock-data-search.png)

- Views.py

  Error 429, also known as "Too Many Requests," occurs when a user sends too many requests to a server

    ```python
    def search_yfinance_ticker(company_name):
    # un-official yfinance API
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
    print(url)

    try:
        response = requests.get(url)
        time.sleep(2)
        response.raise_for_status()
        data = response.json()

        print(f"Yahoo Finance API response: {data}")

        # extract relevant company
        company_options = [
            {
                "name": item.get("longname", item.get("shortname", "N/A")),
                "ticker": item.get("symbol", "N/A"),
                "exchange": item.get("exchDisp", "N/A")
            }
            for item in data.get("quotes", [])
        ]
        
        return company_options
    except Exception as e:
        print(f"Error fetching ticker for {company_name}: {e}")
        return []
        ```
        