FROM python:3.12-slim

WORKDIR /app

# ddddocr / onnxruntime 运行依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY py/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    || pip install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

COPY py/ .
COPY json/ /app/json/

ENTRYPOINT ["python"]
CMD ["get_seat_tomorrow_mode_1.py"]
