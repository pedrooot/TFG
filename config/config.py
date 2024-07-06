import requests
from colorama import Fore, Style

glucose_bot_version = "v1.0.0"
def check_current_version():
    print_banner()
    try:
        release_response = requests.get("https://api.github.com/repos/pedrooot/TFG/releases/latest")
        latest_version = release_response.json()["tag_name"]
        if glucose_bot_version != latest_version:
            print(f"New version available: {latest_version}")
            exit(0)
        else:
            print("You are using the latest version.")
            exit(0)
    except requests.exceptions.RequestException as e:
        print("Error checking for updates.")
        print(e)
        exit(1)
    except KeyError as e:
        print("Error checking for updates.")
        print(e)
        exit(1)

def print_help(message=None):
    print_banner()
    if message:
        print(message)
    print("Usage: glucosebot [-h] [-v]")
    print("GlucoseBot is a tool to help you manage your diabetes.")
    print("For more information, visit: https://github.com/pedrooot/TFG")


def print_banner():
    banner = rf""" {Fore.YELLOW}
  ________.__                                  __________        __   
 /  _____/|  |  __ __   ____  ____  ______ ____\______   \ _____/  |_ 
/   \  ___|  | |  |  \_/ ___\/  _ \/  ___// __ \|    |  _//  _ \   __\
\    \_\  \  |_|  |  /\  \__(  <_> )___ \\  ___/|    |   (  <_> )  |  
 \______  /____/____/  \___  >____/____  >\___  >______  /\____/|__|  
        \/                 \/          \/     \/       \/           {Style.RESET_ALL}  
{Fore.BLUE}Version: {glucose_bot_version}{Style.RESET_ALL} """
    print(banner)