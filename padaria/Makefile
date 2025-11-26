# Define que estes comandos não são arquivos reais
.PHONY: setup-network run start clean-network



setup-network:
	@echo "--- Configurando IPTables (Porta 80 -> 8000) ---"
	sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
	sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000
	@echo "--- Rede Configurada ---"

run:
	@echo "--- Gerando Migrations ---"
	python3 manage.py makemigrations
	@echo "--- Aplicando Migrations ---"
	python3 manage.py migrate
	@echo "--- Iniciando Servidor (Acesse: http://localhost) ---"
	python3 manage.py runserver 0.0.0.0:8000


start: setup-network run


clean-network:
	sudo iptables -D INPUT -p tcp --dport 80 -j ACCEPT
	sudo iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000
	@echo "--- Regras de rede removidas ---"
