from bs4 import BeautifulSoup
import requests
import time
from ids_utils.passwd_encrypt import generate_encrypted_password
from ids_utils.captcha_ocr import get_ocr_res
import logging

session = requests.session()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("开始打印日志")

LOGIN_URI = (
    "http://ids.qfnu.edu.cn/authserver/login"
    "?service=http%3A%2F%2Flibyy.qfnu.edu.cn%2Fapi%2Fcas%2Fcas"
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/117.0.5938.63 Safari/537.36"
)


def _login_headers():
    return {
        "User-Agent": USER_AGENT,
        "Referer": LOGIN_URI,
    }


def _parse_login_error(html):
    soup = BeautifulSoup(html, "html.parser")
    for err_id in ("showErrorTip", "authError", "errorTip", "msg"):
        el = soup.find(id=err_id)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    for keyword in (
        "验证码错误",
        "验证码不正确",
        "验证码失效",
        "密码错误",
        "用户名或密码",
        "账号或密码",
    ):
        if keyword in html:
            return keyword
    return None


def get_salt_and_execution():
    """
    获取盐值和执行数据

    Returns:
        tuple: (盐值, 执行数据)
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "http://libyy.qfnu.edu.cn/",
    }
    response_data = session.get(url=LOGIN_URI, headers=headers).text
    soup_decoded_data = BeautifulSoup(response_data, "html.parser")
    execution_el = soup_decoded_data.find(id="execution")
    salt_el = soup_decoded_data.find(id="pwdEncryptSalt")
    if execution_el is None:
        raise ValueError("登录页未找到 execution 字段")
    execution_data = execution_el.get("value")
    salt_data = salt_el.get("value") if salt_el else ""
    return salt_data, execution_data


def captcha_check(username):
    """
    检查是否需要验证码

    Args:
        username (str): 用户名

    Returns:
        bool: 是否需要验证码
    """
    uri = "http://ids.qfnu.edu.cn/authserver/checkNeedCaptcha.htl"
    headers = {"User-Agent": USER_AGENT}
    data = {"username": username, "_": int(round(time.time() * 1000))}
    res = session.get(url=uri, params=data, headers=headers)
    return "true" in res.text


def get_captcha():
    """
    获取验证码

    Returns:
        bytes: 验证码图片的字节内容
    """
    uri = "http://ids.qfnu.edu.cn/authserver/getCaptcha.htl?" + str(
        int(round(time.time() * 1000))
    )
    headers = _login_headers()
    res = session.get(url=uri, headers=headers)
    return res.content


def get_token(username, password, max_attempts=25):
    """
    获取用户 Token

    Args:
        username (str): 用户名
        password (str): 密码
        max_attempts (int): 登录最大尝试次数（验证码识别错误时会重试）

    Returns:
        str: IDS 登录成功后的 Location 跳转地址
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": LOGIN_URI,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    for attempt in range(1, max_attempts + 1):
        session.cookies.clear()
        cap_res = ""
        salt, execution_data = get_salt_and_execution()
        need_captcha = captcha_check(username)
        if need_captcha:
            logger.info(f"需要验证码，第 {attempt}/{max_attempts} 次尝试识别")
            try:
                cap_pic = get_captcha()
                cap_res = get_ocr_res(cap_pic)
                logger.info(f"验证码识别结果: {cap_res}")
            except Exception as e:
                logger.error(f"获取或识别验证码失败: {e}")
        else:
            logger.info("无需验证码，尝试 IDS 登录")

        enc_passwd = generate_encrypted_password(password, salt)
        data = {
            "username": username,
            "password": enc_passwd,
            "captcha": cap_res,
            "_eventId": "submit",
            "cllt": "userNameLogin",
            "dllt": "generalLogin",
            "lt": "",
            "execution": execution_data,
        }
        res = session.post(
            url=LOGIN_URI, headers=headers, data=data, allow_redirects=False
        )
        location = res.headers.get("Location")
        if location:
            return location

        err_hint = _parse_login_error(res.text)
        logger.warning(
            f"IDS 登录未返回跳转 (第 {attempt}/{max_attempts} 次)"
            f"，HTTP {res.status_code}"
            + (f"，页面提示: {err_hint}" if err_hint else "")
        )
        if not need_captcha:
            break
        time.sleep(0.3)

    raise ValueError("IDS 登录失败")


if __name__ == "__main__":
    get_token("", "")
