# Dockerfile
#FROM python:3.11-slim

# 作業ディレクトリを設定
#WORKDIR /app

# ホストのファイルをコンテナにコピー
#COPY . /app

# 必要なパッケージをインストール
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt

# 静的ファイルを収集
#RUN python manage.py collectstatic --noinput

# ポートを指定（Djangoデフォルト8000）
#EXPOSE 8000

# アプリを起動
#CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
# Pythonイメージを指定
FROM python:3.11

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# ポートを公開（例: 8000）
EXPOSE 8000

# アプリを起動
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]