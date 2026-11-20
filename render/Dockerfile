FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit==1.67.0 supabase==2.34.1
COPY app.py .
CMD ["sh", "-c", "exec streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true --browser.gatherUsageStats=false"]
