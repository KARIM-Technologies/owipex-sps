import os
import subprocess
import json

def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Ausführung von {command}: {e}")

def get_input(prompt, double_check=False):
    while True:
        value = input(prompt)
        if not double_check:
            return value
        value_verify = input(prompt + " wiederholen: ")
        if value == value_verify:
            return value
        else:
            print("Eingaben stimmen nicht überein, bitte erneut versuchen.")

def install_and_start_service(script_path):
    run_command(f"chmod +x {script_path}")
    run_command(script_path)

def adjust_tb_edge_conf(tb_edge_conf_path, cloud_rpc_host, cloud_rpc_port, cloud_routing_key, cloud_routing_secret, postgres_password):
    with open(tb_edge_conf_path, 'r') as file:
        lines = file.readlines()
    
    new_lines = []
    for line in lines:
        if "CLOUD_ROUTING_KEY" in line:
            new_lines.append(f'{cloud_routing_key}\n')
        elif "CLOUD_ROUTING_SECRET" in line:
            new_lines.append(f'{cloud_routing_secret}\n')
        elif "CLOUD_RPC_HOST" in line:
            new_lines.append(f'{cloud_rpc_host}\n')
        elif "CLOUD_RPC_PORT" in line:
            new_lines.append(f'{cloud_rpc_port}\n')
        elif "SPRING_DATASOURCE_URL" in line:
            new_lines.append('export SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/owipex_db\n')
        elif "SPRING_DATASOURCE_USERNAME" in line:
            new_lines.append('export SPRING_DATASOURCE_USERNAME=postgres\n')
        elif "SPRING_DATASOURCE_PASSWORD" in line:
            new_lines.append(f'export SPRING_DATASOURCE_PASSWORD="{postgres_password}"\n')
        else:
            new_lines.append(line)

    with open(tb_edge_conf_path, 'w') as file:
        file.writelines(new_lines)

def copy_netplan_config(source_path, destination_path="/etc/netplan/00-installer-config.yaml"):
    try:
        with open(source_path, 'r') as src:
            config = src.read()
        with open(destination_path, 'w') as dst:
            dst.write(config)
        run_command("sudo netplan apply")
    except IOError as e:
        print(f"Fehler beim Kopieren der Netplan-Konfigurationsdatei: {e}")

def modify_thingsboard_gateway_config(config_path, hostname):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        config['host'] = "146.190.179.185"
        config['accessToken'] = f"WbXgAAte2{hostname}"
        with open(config_path, 'w') as file:
            json.dump(config, file, indent=4)
    except IOError as e:
        print(f"Fehler beim Lesen/Schreiben der Thingsboard Gateway-Konfigurationsdatei: {e}")
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der Thingsboard Gateway-Konfigurationsdatei: {e}")

def main():
    hostname = get_input("Bitte geben Sie den gewünschten Hostnamen ein (924XXXX): ")
    os.system(f"sudo hostnamectl set-hostname {hostname}")

    source_netplan_path = "/home/owipex_adm/owipex-sps/Installer/NetworkConf/IPConf/01-netcfg.yaml"
    copy_netplan_config(source_netplan_path)

    tb_edge_conf_path = "/etc/tb-edge/conf/tb-edge.conf"
    cloud_rpc_host = 'export CLOUD_RPC_HOST="146.190.179.185"'
    cloud_rpc_port = 'export CLOUD_RPC_PORT="7070"'
    cloud_routing_key = f'export CLOUD_ROUTING_KEY="{get_input("Bitte CLOUD_ROUTING_KEY eingeben: ", True)}"'
    cloud_routing_secret = f'export CLOUD_ROUTING_SECRET="{get_input("Bitte CLOUD_ROUTING_SECRET eingeben: ", True)}"'
    postgres_password = get_input("Bitte SPRING_DATASOURCE_PASSWORD eingeben: ", True)

    adjust_tb_edge_conf(tb_edge_conf_path, cloud_rpc_host, cloud_rpc_port, cloud_routing_key, cloud_routing_secret, postgres_password)

    tb_gateway_config_path = "/etc/thingsboard-gateway/config/tb_gateway.yaml"
    modify_thingsboard_gateway_config(tb_gateway_config_path, hostname)

    run_command("sudo systemctl disable h2o_watchdog.service")
    installer_script_path = "/home/owipex_adm/owipex-sps/Installer/watchdog/powerWatchdogInstaller.sh"
    install_and_start_service(installer_script_path)

    print("Anpassungen abgeschlossen.")

if __name__ == "__main__":
    main()
