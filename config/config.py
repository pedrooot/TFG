from colorama import Fore, Style

glucose_bot_version = "v1.0.0"


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
