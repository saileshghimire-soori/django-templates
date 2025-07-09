# Default IP and Port
default_ip="127.0.0.1"
default_port="8000"

# Regex for matching IP address (IPv4)
ip_regex='^([0-9]{1,3}\.){3}[0-9]{1,3}$'
# Regex for matching port (a number between 1 and 65535)
port_regex='^[0-9]+$'

server=$1
port=$2

# Function to run the server
runserver() {
    local ip=$1
    local port=$2
    echo "Starting server at $ip:$port"
    python manage.py runserver "$ip:$port"
}

# Function to get the IP address of the wifi interface
get_wifi_ip() {
    python -c "
import socket
import sys

def get_wifi_ip():
    hostname = socket.gethostname()
    
    ip_address = socket.gethostbyname(hostname)
    
    if ip_address:
        print(ip_address)
    else:
        sys.exit('Could not fetch IP address for Wi-Fi interface')

get_wifi_ip()
"
}
# Detect the operating system
os_type=$(uname)

# Check if both server and port are provided
if [[ "$server" =~ $ip_regex ]] && [[ "$port" =~ $port_regex ]]; then
    # Case: Both server (IP) and port are provided
    runserver "$server" "$port"

# If only one argument is given, check which one is an IP or port
elif [[ "$server" =~ $port_regex ]]; then
    # Case: Only port is provided, use default IP
    runserver "$default_ip" "$server"
elif [[ "$server" == "localhost" ]]; then
    # Case: Only "localhost" is provided, use localhost:port
    runserver "localhost" "$default_port"
elif [[ "$server" =~ $ip_regex ]]; then
    # Case: Only server (IP) is provided, use default port
    runserver "$server" "$default_port"
# elif [[ "$server" == "wifi" ]]; then
elif [[ "$server" =~ ^[a-zA-Z]+$ ]]; then
    # Case: 'wifi' is provided, get the IP address of the wifi interface
    wifi_ip=$(get_wifi_ip "$os_type")
    if [[ -z "$wifi_ip" ]]; then
        echo "$os_type"
        echo "Could not find IP address for wifi interface."
        exit 1
    fi
    runserver "$wifi_ip" "$port"
else
    # Case: Neither server nor port provided, use default IP and port
    runserver "$default_ip" "$default_port"
fi
