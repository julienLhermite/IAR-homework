all:
	@echo "Les cibles valides sont : dynamic_programming q_learning ou monte_carlo"

q_learning: main.py
	./main.py q_learning

dynamic_programing: main.py
	./main.py dynamic_programming

monte_carlo: main.py
	./main.py monte_carlo
