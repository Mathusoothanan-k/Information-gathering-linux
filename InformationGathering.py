import re
import subprocess

def print_red(text):
    return f"\033[91m{text}\033[0m"

def print_green(text):
    return f"\033[92m{text}\033[0m"

def print_yellow(text):
    return f"\033[93m{text}\033[0m"

class Informate:

    @staticmethod
    def analyze_ping_input(user_input):
        ip_address_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

        # Use match method to check if the input matches the pattern
        if ip_address_pattern.match(user_input):
            host = user_input
            print(print_red("Input is already an IP address: ") + f" {user_input}")
            print(print_green("Try to give the domain name for more information !!!"))
            return host
        else:
            try:
                result = subprocess.run(['ping', '-c', '4', user_input], capture_output=True, text=True, check=True)
                mano = result.stdout
                host = user_input
                print(print_red("Ping output for: "), end="")
                print(print_green(user_input))
                print(mano)

                # Extract unique IP addresses from the ping output
                ip_addresses_set = set(ip_address_pattern.findall(mano))

                # Print extracted unique IP addresses
                if ip_addresses_set:
                    print(print_red("Extracted IP addresses: "), end="")
                    for ip in ip_addresses_set:
                        print(print_green(ip))
                else:
                    print(print_red("No IP addresses found in the ping output."))
                return host
            except subprocess.CalledProcessError as e:
                if e.returncode == 2:
                    print(f"Error executing ping: {e}.")
                    print(print_red("The provided IP or domain name is invalid."))
                else:
                    print(print_red(f"Error executing ping: {e}"))
                return None

    @staticmethod
    def nslookup(host, query_type):
        try:
            result = subprocess.run(['nslookup', f'-query={query_type}', host],
                                    capture_output=True, text=True, check=True)
            output_lines = result.stdout.split('\n')

            print(print_red(f"\n----------> {query_type.capitalize()} Records <----------\n"))
            for line in output_lines:
                if "Set options:" in line or "Non-authoritative answer:" in line or "Authoritative answers can be found from:" in line:
                    print(print_red(line))
                else:
                    print(print_green(line))

        except subprocess.CalledProcessError as e:
            print(print_red(f"Error executing nslookup ({query_type}): {e}"))

    @staticmethod
    def nmap(target, option):
        print(print_red("Running nmap for target:"), target)
        nmap_options = []

        match option.lower():
            case "y":
                print(print_yellow("Enter the Flag \n "))
                print(print_red("Scan all the ports "), end="")
                print(print_yellow("('all')"))
                print(print_red("\nspecific port scanning "), end="")
                print(print_yellow("('P'/'p')"))
                print(print_red("\nOS identification "), end="")
                print(print_yellow("('OS'/'os')"))
                print(print_red("\nTraceroute "),end="")
                print(print_yellow("('T'/'t')"))
                print(print_green("\n$>>"),end="")
                match input(print_red("Enter the flag: ")).lower():
                    case "p":
                        ports = input("Enter range of ports or specific ports (comma-separated): ")
                        ports = ports.replace(" ", "")
                        nmap_options.extend(['-p', ports])
                    case "os":
                        nmap_options.append('-O')
                    case "all":
                        print(print_green("Please wait for a while..."))
                        nmap_options.extend(['-v', '-A', '-Pn'])
                    case "t":
                        nmap_options.append('-trace')
                    case _:
                        print(print_red("Invalid scanning process."))
                        return option.lower()

            case "n":
                nmap_options.extend(['--open', '-sS'])  # Add -sS flag for TCP SYN scan
            case _:
                print(print_red("Invalid option. Please choose either 'Y' or 'N'."))
                return None

        command = ['sudo', 'nmap'] + nmap_options + [target]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output_lines = result.stdout.split('\n')

            for line in output_lines:
                if "open"in line:
                    print(print_yellow(line))
                else:
                    print(line)
        except subprocess.CalledProcessError as e:
            print(print_red(f"Error executing nmap: {e}"))
            print(print_red("Detailed error information:"))
            print(print_red(e.stderr))  # Print the standard error output for more details

    @staticmethod
    def trace_host(host):
        # Run the dig command to trace DNS for the host
        dig_command = f"dig +trace {host}"
        dig_output = subprocess.check_output(dig_command, shell=True, text=True)
        print(print_red(f"\n----------> DNS TRACE <----------\n"))
        print(dig_output)

        # Run the traceroute command for network tracing
        traceroute_command = f"traceroute {host}"
        traceroute_output = subprocess.check_output(traceroute_command, shell=True, text=True)
        print("\nNetwork Tracing:")
        print(traceroute_output)
        

# Example usage
user_input = input("Give the IP or a domain name: ")
host = Informate.analyze_ping_input(user_input)

if host is not None:
    Informate.nslookup(host, 'ns')
    Informate.nslookup(host, 'mx')
    Informate.trace_host(host)
    print(print_red("Give your opinion, did you need to scan all ports or only you need to see the open ports?\n"))
    while True:
        print(print_green("Press 'Y' to see all ports or 'N' to see only open ports: "), end="")
        option = input(print_yellow("('Y'/'N') : "))
        if option.lower() in ['y', 'n']:
            break
        else:
            print(print_red("Invalid option. Please choose either 'Y' or 'N'."))
    Informate.nmap(host, option)
