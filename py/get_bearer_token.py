import json
import logging
import os
import yaml

from get_ids_token import get_token, session as ids_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS_GET = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/117.0.5938.63 Safari/537.36"
}


def get_bearer_token(username, password):
    """
    获取 CAS 登录的 Bearer Token
    :return: (姓名, Token)
    """
    try:
        ids_token = get_token(username, password)

        ids_session.get(url=ids_token, headers=HEADERS_GET, allow_redirects=False)
        res = ids_session.get(
            url="http://libyy.qfnu.edu.cn/api/cas/cas",
            headers=HEADERS_GET,
            allow_redirects=False,
        )
        location = res.headers.get("Location")
        if not location:
            raise ValueError("图书馆 CAS 未返回 Location")
        cas_token = location[-32:]

        data = {"cas": cas_token}
        headers_post = {
            "User-Agent": HEADERS_GET["User-Agent"],
            "Content-Type": "application/json",
        }
        res = ids_session.post(
            url="http://libyy.qfnu.edu.cn/api/cas/user",
            headers=headers_post,
            data=json.dumps(data),
        )
        parsed_res = json.loads(res.text)

        return parsed_res["member"]["name"], parsed_res["member"]["token"]
    except Exception as e:
        logger.error(f"获取 Bearer Token 失败: {e}")
        return None, None


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    name, token = get_bearer_token(config["USERNAME"], config["PASSWORD"])
    if name and token:
        print("登录成功，姓名:", name)
    else:
        print("登录失败")
