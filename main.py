from fastapi import FastAPI, HTTPException
import httpx
from collections import deque
import time

app = FastAPI()

WINDOW_SIZE = 10
API_TIMEOUT = 0.5  
THIRD_PARTY_API = {
    "p": "http://20.244.56.144/test/primes",
    "f": "http://20.244.56.144/test/fibo",
    "e": "http://20.244.56.144/test/even",
    "r": "http://20.244.56.144/test/rand"
}
numbers_store = deque(maxlen=WINDOW_SIZE)
def fetch_numbers(number_type: str):
    try:
        start_time = time.time()
        response = httpx.get(THIRD_PARTY_API[number_type], timeout=API_TIMEOUT)
        if response.status_code == 200:
            return response.json().get("numbers", [])
    except httpx.RequestError:
        return [] 
    return []

@app.get("/numbers/{number_type}")
def get_numbers(number_type: str):
    if number_type not in THIRD_PARTY_API:
        raise HTTPException(status_code=400, detail="Invalid number type")
    prev_state = list(numbers_store) 
    new_numbers = fetch_numbers(number_type)
    for num in new_numbers:
        if num not in numbers_store:
            numbers_store.append(num)
    avg = round(sum(numbers_store) / len(numbers_store), 2) if numbers_store else 0.0
    return {
        "windowPrevState": prev_state,
        "windowCurrState": list(numbers_store),
        "numbers": new_numbers,  
        "avg": avg
    }
