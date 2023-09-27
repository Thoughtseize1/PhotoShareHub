from aiohttp import ClientSession, ContentTypeError
from fastapi import Request


async def send_post_request(request: Request, data: str, request_url: str):
    try:
        url = f"{request.base_url}{request_url}"
        headers = {
            "Content-Type": "application/json",
        }

        data_key = "token" if request_url == "auth/verify" else "email"
        data = {data_key: data}

        async with ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_data = await response.json()

                if response.status == 200 and request_url == "auth/verify":
                    return {"status": "Your email has been verified"}
                elif "token" in request_url and response.status == 202:
                    return {
                        "status": "Email with instructions has been sent to your email box."
                    }
                else:
                    print(f"Помилка: {response.status}")
                    print(f"Текст відповіді: {response_data}")
                    return {"error": "Something went wrong"}
    except ContentTypeError as e:
        print(f"Помилка при обробці JSON: {e}")
        return {"error": "Error processing JSON"}
    except Exception as e:
        print(f"Помилка: {e}")
        return {"error": "An error occurred"}
