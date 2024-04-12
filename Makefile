


run:
	uvicorn main:app --reload


consumers:
	python3 infrastructure/queue/consumer.py

.PHONY: run, consumers
