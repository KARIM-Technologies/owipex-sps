import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Ändere dies in einen sicheren Schlüssel

logging.basicConfig(level=logging.DEBUG)

# Flask-Login Konfiguration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dummy Benutzer
users = {'admin': {'password': 'password123'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    ssid, password = read_hotspot_settings()
    hostname = read_hostname()
    edge_key, edge_secret, edge_db_password, cloud_rpc_host, spring_datasource_url = read_tb_edge_conf()
    access_token = read_env_file()
    logging.debug(f"SSID: {ssid}, Password: {password}, Hostname: {hostname}, EDGE Key: {edge_key}, EDGE Secret: {edge_secret}, EDGE DB Password: {edge_db_password}, CLOUD RPC Host: {cloud_rpc_host}, SPRING DATASOURCE URL: {spring_datasource_url}, Access Token: {access_token}")  # Protokolliere die gelesenen Werte
    return render_template('index.html', ssid=ssid, password=password, hostname=hostname, edge_key=edge_key, edge_secret=edge_secret, edge_db_password=edge_db_password, cloud_rpc_host=cloud_rpc_host, spring_datasource_url=spring_datasource_url, access_token=access_token)

@app.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    ssid = request.form['ssid']
    password = request.form['password']
    hostname = request.form['hostname']
    edge_key = request.form['edge_key']
    edge_secret = request.form['edge_secret']
    edge_db_password = request.form['edge_db_password']
    cloud_rpc_host = request.form['cloud_rpc_host']
    spring_datasource_url = request.form['spring_datasource_url']
    access_token = request.form['access_token']
    update_hotspot_settings(ssid, password)
    update_hostname(hostname)
    update_tb_edge_conf(edge_key, edge_secret, edge_db_password, cloud_rpc_host, spring_datasource_url)
    update_env_file(access_token)
    return redirect(url_for('index'))

def read_hotspot_settings():
    config_path = '/etc/NetworkManager/system-connections/Hotspot.nmconnection'
    ssid = ''
    password = ''
    try:
        with open(config_path, 'r') as f:
            for line in f:
                logging.debug(f"Reading line: {line.strip()}")  # Protokolliere jede Zeile
                if line.strip().startswith('ssid='):
                    ssid = line.split('=')[1].strip()
                    logging.debug(f"Found SSID: {ssid}")  # Protokolliere gefundene SSID
                if line.strip().startswith('psk='):
                    password = line.split('=')[1].strip()
                    logging.debug(f"Found Password: {password}")  # Protokolliere gefundenes Passwort
    except Exception as e:
        logging.error(f'Error reading configuration: {e}')
    logging.debug(f'Read SSID: {ssid}, Read Password: {password}')  # Protokolliere die gelesenen Werte
    return ssid, password

def update_hotspot_settings(ssid, password):
    config_content = f"""
    [connection]
    id=Hotspot
    uuid=39785851-0780-430b-a057-72cd6f657d9a
    type=wifi
    autoconnect=false
    interface-name=wlp4s0
    permissions=
    timestamp=1717787614
    autoconnect=true

    [wifi]
    mac-address-blacklist=
    mode=ap
    seen-bssids=C8:8A:9A:FA:9B:8C;
    ssid={ssid}

    [wifi-security]
    group=ccmp;
    key-mgmt=wpa-psk
    pairwise=ccmp;
    proto=rsn;
    psk={password}

    [ipv4]
    dns-search=
    method=shared

    [ipv6]
    addr-gen-mode=stable-privacy
    dns-search=
    method=auto

    [proxy]
    """
    config_path = '/etc/NetworkManager/system-connections/Hotspot.nmconnection'
    with open(config_path, 'w') as f:
        f.write(config_content.strip())
    logging.debug(f'Updated configuration: {config_content.strip()}')
    os.system('sudo chmod 600 ' + config_path)
    os.system('sudo systemctl restart NetworkManager')
    logging.debug('Restarted NetworkManager')

def read_hostname():
    try:
        with open('/etc/hostname', 'r') as f:
            hostname = f.read().strip()
            logging.debug(f'Read Hostname: {hostname}')
            return hostname
    except Exception as e:
        logging.error(f'Error reading hostname: {e}')
        return ''

def update_hostname(hostname):
    try:
        with open('/etc/hostname', 'w') as f:
            f.write(hostname + '\n')
        logging.debug(f'Updated Hostname: {hostname}')
        os.system('sudo hostnamectl set-hostname ' + hostname)
    except Exception as e:
        logging.error(f'Error updating hostname: {e}')

def read_tb_edge_conf():
    config_path = '/etc/tb-edge/conf/tb-edge.conf'
    edge_key = ''
    edge_secret = ''
    edge_db_password = ''
    cloud_rpc_host = ''
    spring_datasource_url = ''
    try:
        with open(config_path, 'r') as f:
            for line in f:
                logging.debug(f"Reading line: {line.strip()}")  # Protokolliere jede Zeile
                if line.strip().startswith('export CLOUD_ROUTING_KEY='):
                    edge_key = line.split('=')[1].strip().strip('"')
                    logging.debug(f"Found EDGE Key: {edge_key}")  # Protokolliere gefundenen EDGE Key
                if line.strip().startswith('export CLOUD_ROUTING_SECRET='):
                    edge_secret = line.split('=')[1].strip().strip('"')
                    logging.debug(f"Found EDGE Secret: {edge_secret}")  # Protokolliere gefundenes EDGE Secret
                if line.strip().startswith('export SPRING_DATASOURCE_PASSWORD='):
                    edge_db_password = line.split('=')[1].strip().strip('"')
                    logging.debug(f"Found EDGE DB Password: {edge_db_password}")  # Protokolliere gefundenes EDGE DB Password
                if line.strip().startswith('export CLOUD_RPC_HOST='):
                    cloud_rpc_host = line.split('=')[1].strip().strip('"')
                    logging.debug(f"Found CLOUD RPC Host: {cloud_rpc_host}")  # Protokolliere gefundenen CLOUD RPC Host
                if line.strip().startswith('export SPRING_DATASOURCE_URL='):
                    spring_datasource_url = line.split('=')[1].strip().strip('"')
                    logging.debug(f"Found SPRING DATASOURCE URL: {spring_datasource_url}")  # Protokolliere gefundene SPRING DATASOURCE URL
    except Exception as e:
        logging.error(f'Error reading TB Edge configuration: {e}')
    return edge_key, edge_secret, edge_db_password, cloud_rpc_host, spring_datasource_url

def update_tb_edge_conf(edge_key, edge_secret, edge_db_password, cloud_rpc_host, spring_datasource_url):
    config_path = '/etc/tb-edge/conf/tb-edge.conf'
    try:
        with open(config_path, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.strip().startswith('export CLOUD_ROUTING_KEY='):
                new_lines.append(f'export CLOUD_ROUTING_KEY="{edge_key}"\n')
            elif line.strip().startswith('export CLOUD_ROUTING_SECRET='):
                new_lines.append(f'export CLOUD_ROUTING_SECRET="{edge_secret}"\n')
            elif line.strip().startswith('export SPRING_DATASOURCE_PASSWORD='):
                new_lines.append(f'export SPRING_DATASOURCE_PASSWORD="{edge_db_password}"\n')
            elif line.strip().startswith('export CLOUD_RPC_HOST='):
                new_lines.append(f'export CLOUD_RPC_HOST="{cloud_rpc_host}"\n')
            elif line.strip().startswith('export SPRING_DATASOURCE_URL='):
                new_lines.append(f'export SPRING_DATASOURCE_URL="{spring_datasource_url}"\n')
            else:
                new_lines.append(line)

        with open(config_path, 'w') as f:
            f.writelines(new_lines)
        logging.debug(f'Updated TB Edge configuration')
    except Exception as e:
        logging.error(f'Error updating TB Edge configuration: {e}')

def read_env_file():
    env_file_path = '/etc/owipex/.env'
    access_token = ''
    try:
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.strip().startswith('THINGSBOARD_ACCESS_TOKEN='):
                    access_token = line.split('=')[1].strip()
                    logging.debug(f"Found Access Token: {access_token}")
    except Exception as e:
        logging.error(f'Error reading .env file: {e}')
    return access_token

def update_env_file(access_token):
    env_file_path = '/etc/owipex/.env'
    try:
        with open(env_file_path, 'w') as f:
            f.write(f'THINGSBOARD_ACCESS_TOKEN={access_token}\n')
        logging.debug(f'Updated .env file')
    except Exception as e:
        logging.error(f'Error updating .env file: {e}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
