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
    # Skript ausführbar machen
    run_command(f"chmod +x {script_path}")
    # Skript ausführen
    run_command(script_path)

def adjust_tb_edge_conf(tb_edge_conf_path, cloud_rpc_host, cloud_rpc_port, cloud_routing_key, cloud_routing_secret, postgres_password):
    with open(tb_edge_conf_path, 'r') as file:
        lines = file.readlines()
    new_lines = []
    for line in lines:
        if "# export CLOUD_ROUTING_KEY=" in line:
            new_lines.append(cloud_routing_key + "\n")
        elif "# export CLOUD_ROUTING_SECRET=" in line:
            new_lines.append(cloud_routing_secret + "\n")
        elif "# export CLOUD_RPC_HOST=" in line and "demo.thingsboard.io" not in line:
            new_lines.append(cloud_rpc_host + "\n")
        elif "# export CLOUD_RPC_PORT=" in line:
            new_lines.append(cloud_rpc_port + "\n")
        elif "# export SPRING_DATASOURCE_URL=" in line:
            new_lines.append(f"export SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/owipex_db\n")
        elif "# export SPRING_DATASOURCE_USERNAME=" in line:
            new_lines.append("export SPRING_DATASOURCE_USERNAME=postgres\n")
        elif "# export SPRING_DATASOURCE_PASSWORD=" in line:
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
        print(f"Netplan-Konfiguration erfolgreich von {source_path} nach {destination_path} kopiert.")
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
        print(f"Thingsboard Gateway-Konfiguration erfolgreich aktualisiert: {config_path}")
    except IOError as e:
        print(f"Fehler beim Lesen/Schreiben der Thingsboard Gateway-Konfigurationsdatei: {e}")
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der Thingsboard Gateway-Konfigurationsdatei: {e}")

def main():
    hostname = get_input("Bitte geben Sie den gewünschten Hostnamen ein (924XXXX): ")
    os.system(f"sudo hostnamectl set-hostname {hostname}")

    # Pfad zur vorbereiteten Netplan-Konfigurationsdatei anpassen und kopieren
    source_netplan_path = "/home/owipex_adm/owipex-sps/Installer/NetworkConf/IPConf/00-installer-config.yaml"
    copy_netplan_config(source_netplan_path)

    # TB-EDGE-Konfiguration anpassen
    tb_edge_conf_path = "/etc/tb-edge/conf/tb-edge.conf"
    cloud_rpc_host = 'export CLOUD_RPC_HOST="146.190.179.185"'
    cloud_rpc_port = 'export CLOUD_RPC_PORT="7070"'
    cloud_routing_key = f'export CLOUD_ROUTING_KEY="{get_input("Bitte CLOUD_ROUTING_KEY eingeben: ", True)}"'
    cloud_routing_secret = f'export CLOUD_ROUTING_SECRET="{get_input("Bitte CLOUD_ROUTING_SECRET eingeben: ", True)}"'
    postgres_password = get_input("Bitte SPRING_DATASOURCE_PASSWORD eingeben: ", True)

    adjust_tb_edge_conf(tb_edge_conf_path, cloud_rpc_host, cloud_rpc_port, cloud_routing_key, cloud_routing_secret, postgres_password)

    # Thingsboard Gateway-Konfiguration aktualisieren
    tb_gateway_config_path = "/etc/thingsboard-gateway/config/tb_gateway.yaml"
    modify_thingsboard_gateway_config(tb_gateway_config_path, hostname)

    # Alten Service deaktivieren und neuen installieren
    run_command("sudo systemctl disable h2o_watchdog.service")
    installer_script_path = "/home/owipex_adm/owipex-sps/Installer/watchdog/powerWatchdogInstaller.sh"
    install_and_start_service(installer_script_path)

    print("Neuer Service wurde erfolgreich installiert und gestartet.")
    print("Anpassung abgeschlossen.")

if __name__ == "__main__":
    main()
