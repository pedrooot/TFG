import requests

glucose_bot_version = "v1.0.0"
def check_current_version():
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
    if message:
        print(message)
    print("GlucoseBot is a tool to help you manage your diabetes.")
    print("For more information, visit: https://github.com/pedrooot/TFG")