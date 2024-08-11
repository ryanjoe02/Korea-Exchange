import requests
from django.http import JsonResponse
from django.shortcuts import render

API_KEY = 'your_api_key_here'

def get_kospi_data():
    url = f'https://data.krx.com/api/data/KOSPI'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def kospi_view(request):
    data = get_kospi_data()

    # kospi가 -8% 떨어진 최신 날짜 찾기
    latest_drop_date = None
    highest_date = None
    lowest_date = None

    highest_value = float('-inf')
    lowest_value = float('inf')

    previous_value = None

    for record in data:
        current_value = record['kospi_value']
        date = record['date']

        # 1. kospi가 -8% 떨어진 날짜 찾기
        if previous_value:
            drop_percentage = ((previous_value - current_value) / previous_value) * 100
            if drop_percentage >= 8 and not latest_drop_date:
                latest_drop_date = date

        # 2. kospi 최고점 날짜 찾기
        if current_value > highest_value:
            highest_value = current_value
            highest_date = date

        # 3. kospi 최저점 날짜 찾기
        if current_value < lowest_value:
            lowest_value = current_value
            lowest_date = date

        previous_value = current_value

    result = {
        'latest_drop_date': latest_drop_date,
        'highest_date': highest_date,
        'lowest_date': lowest_date,
    }

    return JsonResponse(result)
