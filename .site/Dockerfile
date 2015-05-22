FROM aldryn/cloud-base-project:2.1
WORKDIR /app/
ADD ./ /app/
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput --link