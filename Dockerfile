FROM python
RUN pip3 install kafka-python pandas numpy scipy algorithms mysql
ADD ./actionwrapper.py actionwrapper.py
ADD ./serverless serverless
ENTRYPOINT ["python3", "./actionwrapper.py"]