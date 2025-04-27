# PANDORA - Solução Proposta
TODO: Fazer um README de jeito
TODO: Melhorar a descrição e o processo de instalação  
## Autores
Alexandre Brigolas, 21803430  
Ricardo Nunes, 21805213  

Orientador: Prof. Dr. Pedro Arroz Serra

## Instalação
A instalação deve ser realizada num sistema Linux.
Dependente das permissoes das VMs, pode ser necessario fazer sudo de algumas instrucões em baixo

### Instalar Dependências
```
sudo apt update  
sudo apt install python3 -y  
sudo apt install pipenv -y  
sudo apt install redis-server -y  
sudo apt install mysql-server -y  
sudo apt install libmysqlclient-dev -y  
sudo apt install cmake -y  
sudo apt install git -y  
```
### Instalar o Docker
[Documentação oficial docker](https://docs.docker.com/get-docker/)
[Tutorial para instalação do Docker em Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04-pt)

### Configurar Redis
```
sudo nano /etc/redis/redis.conf
```
Localizar (Ctrl+w): supervised no  
Substituir por: supervised systemd
``` 
sudo systemctl restart redis.service
```
### Testar Redis 
```
sudo systemctl status redis
redis-cli
ping
```
Validar se o output é PONG.
```
exit
```
### Configuração MYSQL
```
sudo su
mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin';
CREATE USER 'django'@'localhost' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON * . * TO 'django'@'localhost';
FLUSH PRIVILEGES;
CREATE SCHEMA pandora;
EXIT
exit
```
root user pw   : admin  
pandora user   : django  
pandora user pw: YOUR_PASSWORD  
### Instalar a Pandora (branch develop)
```
mkdir /path/to/pandora/
cd /path/to/pandora/
mkdir data
git clone --branch develop https://github.com/parroz/pandora
pipenv shell
cd pandora/
pip install -r requirements.txt
```
### Configurar a Pandora
```
cd pandora/
nano local_settings.py
```
O ficheiro local_settings.py tem de ter um aspeto semelhante ao código abaixo.
```
import os

SOCIAL_AUTH_GITHUB_KEY = 'YOUR_GITHUB_APP_KEY'
SOCIAL_AUTH_GITHUB_SECRET = 'YOUR_GITHUB_APP_SECRET'

DB_USER = 'django'
DB_PASSWORD = 'YOUR_PASSWORD'
SECRET_KEY = 'YOUR_SECRET_KEY'
ALLOWED_HOSTS = ['*'] 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pandora',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```
O * permite todos os HOSTS no ALLOWED_HOSTS. Trocar se necessário
Não esquecer de trocar as credênciais para acesso à base de dados.
As keys de github são apenas necessárias se o login for efetuado por lá, caso contrário podem efetuar o login pelo caminho /login/

```
cd ..
python3 manage.py makemigrations
python3 manage.py makemigrations shared
python3 manage.py migrate
```
No comando seguinte, criar um utilizador cujo username seja um email.
```
python3 manage.py createsuperuser
```

```
cd static
gcc ascii.c -o ascii
mv ascii ../../data
cd ..
```

### Criar as imagens Docker
```
cd docker_files/
cd c/
sh build_docker.sh
cd ../java/
sh build_docker.sh
cd ../../
```

### Inicializar workers do Celery
Caso este passo não seja tomado, as submissões não serão processadas  
Executar dentro do pipenv  
Deixar aberto
```
celery -A pandora worker --loglevel=INFO
```

### Executar o pandora
Executar noutra janela cli para não interferir com a do celery
```
cd path/to/pandora/
pipenv shell
cd pandora/
python3 manage.py runserver
```

### Fix devido à criação de user por cli
Como criámos o user por cli, nao foi criado um profile  
A plataforma apresenta erros até ser criado um // TODO: meter isto no zenkit e corrigir  
Navegar ate /admin-django/  
Fazer login  
Clicar em users  
Editar o user  
Completar a ultima secção, e selecionar 'valid'  
Submeter  



# Arranque com a versão dockerized
# AVISO: em certas pode VMs pode requerer sudo
1. Instalar o docker e o docker-compose

2. Arranque:
```bash
docker-compose up -d --remove-orphans
```
ls

3. Build da imagem do docker de execução
```bash
cd docker_files/c/
sh build_docker.sh
```

#Os links em baixo Em certos casos funciona com https
4. Aceder a http://127.0.0.1:8010/
user: admin, password: admin


5. Aceder a http://127.0.0.1:8010/admin

6. Aceder a http://127.0.0.1:8010/admin-django
# TFC-DEISI2112-NicePandora
