# Dockerfile
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# ホストのファイルをコンテナにコピー
COPY . /app

# 必要なパッケージをインストール
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput

# ポートを指定（Djangoデフォルト8000）
EXPOSE 8000

# アプリを起動
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]