import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Test 1: Wrong email, any password
        res1 = await client.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "wronguser@domain.com", "password": "Comply@2025"})
        print("TEST 1 (Wrong Email) STATUS:", res1.status_code, "| RESP:", res1.json())

        # Test 2: Right email, wrong password
        res2 = await client.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@complysense.io", "password": "WrongPassword123"})
        print("TEST 2 (Wrong Password) STATUS:", res2.status_code, "| RESP:", res2.json())

        # Test 3: Right email, right password
        res3 = await client.post("http://127.0.0.1:8000/api/v1/auth/login", json={"email": "admin@complysense.io", "password": "Comply@2025"})
        print("TEST 3 (Valid Credentials) STATUS:", res3.status_code, "| RESP ROLE:", res3.json().get("user", {}).get("role_name"))

if __name__ == '__main__':
    asyncio.run(main())
