# ベースイメージを指定
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# ホストのファイルをコンテナにコピー
COPY . /app/

# 必要なパッケージをインストール
RUN pip install --upgrade pip

# requirements.txt をコンテナにコピーして依存パッケージをインストール
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# 静的ファイルを収集（settings.pyのSTATIC_ROOTを確認してください）
RUN python manage.py collectstatic --noinput

# ポートを指定（Djangoデフォルト8000）
EXPOSE 8000

# アプリを起動（gunicornを使用）
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]