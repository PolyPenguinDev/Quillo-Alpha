#!/usr/bin/env python
import argparse
import requests
from bs4 import BeautifulSoup
import os
import re
import json
import html2text

# Define global constant
TAB_FILE = "tabs.json"


CIRCLE_MAP = {"1":"❶","2":"❷","3":"❸","4":"❹","5":"❺","6":"❻","7":"❼","8":"❽","9":"❾","0":"⓿"}
UB_CIRCLE_MAP = {"1":"①","2":"②","3":"③","4":"④","5":"⑤","6":"⑥","7":"⑦","8":"⑧","9":"⑨","0":"⓪"}
# Initialize HTML to Text converter
html_to_text = html2text.HTML2Text()
html_to_text.ignore_links = False
def newtab():
    return """     _
 ╭──╱ |    ___       _ _ _     
 | ╱ ╱ |  / _ \ _  _(_) | |___ 
 |╱╱   | ▕ (_) | || | | | / _ \\
 ▀─────╯  \__\_\\\\_,_|_|_|_\___/
 NEW TAB
Use \033[1m\033[3mquillo -s "query"\033[0m to search google
Use \033[1m\033[3mquillo -o -f "URL"\033[0m to open a website in a new tab.
Use \033[1m\033[3mquillo -g -f "URL"\033[0m to open a website in a this tab.
Use \033[1m\033[3mquillo -t TAB\033[0m to change the tab.
Use \033[1m\033[3mquillo -c TAB\033[0m to close a tab.
                                  

                       """
def boldify(text):
    """
    Replace characters in the text with their bold equivalents using the BOLD_MAP.
    """
    bold_text = ""
    for line in text.split("\n"):
        ins = 0
        is_bold = True
        line_z = True
        t = ""
        for char in line:
            if is_bold:
                if ins == 2:
                    if char != "#":
                        line_z = False
                elif ins <= 1:
                    is_bold = char == "#"
                    line_z = line_z and is_bold
                    if char != "#":
                        t += char
                else:
                    t += char
            else:
                t += char
            ins += 1
        if is_bold and len(t) > 2:
            t = "\033[1m" +t +"\033[0m"
        if bold_text != "":
            bold_text += "\n" + t
            if line_z and len(t) > 2:
                bold_text += "\n───────────────────────────────────────────────────────────────────"
        else:
            bold_text = t
    return bold_text

def replace_bullets_with_symbol(markdown_text, symbol='•'):
    """
    Replace bullet points in the markdown text with the specified symbol.
    """
    pattern = r'^\s*[-*+]'
    return re.sub(pattern, symbol, markdown_text, flags=re.MULTILINE)

def replace_links(markdown):
    """
    Replace links in the markdown text and extract them for future reference.
    """
    link_pattern = re.compile(r'\[([^]]+)\]\(([^)]+)\)')
    matches = link_pattern.findall(markdown)
    link_list = [[] for _ in range(len(matches))]

    for i, (text, link) in enumerate(matches, start=1):
        reference = f'{text} [{i}]'
        link_list[i - 1].append(link)
        markdown = link_pattern.sub(reference, markdown, 1)

    return markdown, link_list

def remove_tags(html):
    """
    Remove specified tags from the HTML content.
    """
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(['style', 'script', 'img']):
        data.decompose()
    return soup.prettify()

def clear_console():
    """
    Clear the console screen.
    """
    if load_tabs()["clear"]:
        os.system('cls' if os.name == 'nt' else 'clear')

def load_tabs():
    """
    Load tabs data from the file.
    """
    with open(TAB_FILE, 'r') as f:
        return json.load(f)

def save_tabs(tabs_data):
    """
    Save tabs data to the file.
    """
    with open(TAB_FILE, 'w') as f:
        json.dump(tabs_data, f)

def main():
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="A simple command-line program.")
    parser.add_argument("site", help="The website to view.")
    parser.add_argument("-o", "--open", action="store_true", help="Opens a website in a new tab.")
    parser.add_argument("-t", "--tab", action="store_true", help="Switches tab.")
    parser.add_argument("-f", "--format", action="store_true", help="Formats HTML into a more readable format")
    parser.add_argument("-g", "--go", action="store_true", help="Switches the current tab to a new website.")
    parser.add_argument("-s", "--search", action="store_true", help="Searches something on google.")
    parser.add_argument("-c", "--close", action="store_true", help="closes a tab.")
    parser.add_argument("-a", "--advanced", action="store_true", help="changes advanced settings.")

    args = parser.parse_args()

    tabs_data = load_tabs()

    if args.open or args.go:
        clear_console()
        if args.site.isdigit():
            args.site = tabs_data["tabs"][tabs_data["current"] - 1]["links"][int(args.site) - 1][0]
        else:
            args.site = f"http://www.{args.site}" if not args.site.startswith('http') else args.site
        print(f"Loading {args.site} ...")
        response = requests.get(args.site)
        soup = BeautifulSoup(response.content, 'html.parser')
        formatted_html = remove_tags(soup.prettify())
        if args.format:
            title = soup.title.text.strip()
            clear_console()
            job_elements = soup.find_all()
            formatted_html = replace_bullets_with_symbol(html_to_text.handle(formatted_html))
            formatted_html_old = formatted_html
            formatted_html = boldify(replace_links(formatted_html)[0])
        else:
            title = soup.title.text.strip()
            clear_console() 
            formatted_html = soup.prettify()
        if args.open:
            if args.format:
                tabs_data["tabs"].append({"title": title, "links": replace_links(formatted_html)[1], "content": formatted_html})
            else:
                tabs_data["tabs"].append({"title": title, "links": [], "content": formatted_html})
            tabs_data["current"] = len(tabs_data["tabs"])
        else:
            if args.format:
                tabs_data["tabs"][tabs_data["current"] - 1] = {"title": title, "links": replace_links(formatted_html_old)[1], "content": formatted_html}
            else:
                tabs_data["tabs"][tabs_data["current"] - 1] = {"title": title, "links": [], "content": formatted_html}
        print_tabs(tabs_data)
        with open(TAB_FILE, 'w') as f:
            json.dump(tabs_data, f)
    elif args.tab:
        clear_console()
        tabs_data["current"] = int(args.site)
        print_tabs(tabs_data)
        with open(TAB_FILE, 'w') as f:
            json.dump(tabs_data, f)
    elif args.search:
        clear_console()
        args.site = f"http://www.google.com/search?q={args.site}"
        print(f"Loading {args.site} ...")
        response = requests.get(args.site)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.text.strip()
        clear_console()
        content = """
   ___                  _     
  /  _|  ___  ___  __ _| |___ 
 ▕  (| |/ _ \/ _ \/ _` | / -_)
  \____|\___/\___/\__, |_\___|
                  |___/      
              """
        rso_div = soup.find('div', id='main')
        nested_divs = rso_div.find_all('div')
        links = []
        for nested_div in nested_divs:
            a_tag = nested_div.find('a')
            if a_tag:
                try:
                    link_text = a_tag.get("href")
                    soupp = BeautifulSoup(a_tag.prettify(), 'html.parser')
                    text_content = soupp.find('h3', class_='zBAuLc l97dzf').div.text
                    content += f"{text_content} [{str(len(links) + 1)}]"
                    links.append(["https://www.google.com/" + link_text])
                except:
                    pass
        tabs_data["tabs"].append({"title": title, "content": content, "links": links})
        tabs_data["current"] = len(tabs_data["tabs"])
        print_tabs(tabs_data)
        with open(TAB_FILE, 'w') as f:
            json.dump(tabs_data, f)
    elif args.close:
        tabs_data = close_tab(tabs_data, int(args.site))
        with open(TAB_FILE, 'w') as f:
            json.dump(tabs_data, f)
    elif args.advanced:
        if args.site == "help":
            print("""How to use Quillo -a
                  
Usage: \033[1m\033[3mquillo -a \"SETTING=VALUE\"\033[0m
                  
Settings:
    •\033[1m\033[3mclear\033[0m - clear the console when running commands""")
        elif args.site.startswith("clear="):
            e = load_tabs()
            if "True" in args.site:
                e["clear"] = True
            else:
                e["clear"] = False
            save_tabs(e)

def print_tabs(tabs_data):
    """
    Print the tabs data to the console.
    """
    print(f"\n---------⃝🖋️ Quillo Text-Based Browser---------")
    n = 0
    s = "|"
    for tab in tabs_data["tabs"]:
        n += 1
        p= str(n)
        if n == tabs_data["current"]:
            p2 = ""
            for i in p:
                p2+=CIRCLE_MAP[i]
            p = p2
        else:
            p2 = ""
            for i in p:
                p2+=UB_CIRCLE_MAP[i]
            p = p2
        s += f" {p} {tab['title']} |"
    print("\n" + "─" * len(s))
    print(s)
    print("─" * len(s) + "\n")
    print(tabs_data["tabs"][tabs_data["current"] - 1]["content"])

def close_tab(tabs_data, tab_index):
    """
    Close the specified tab.
    """
    if tab_index <= tabs_data["current"]:
        tabs_data["current"] -= 1
    if tabs_data["current"] ==0:
        tabs_data["current"] = 1
    tabs_data["tabs"].pop(tab_index - 1)
    clear_console()
    if len(tabs_data["tabs"]) == 0:
        tabs_data["tabs"].append({"title":"New Tab", "content":newtab()})
    print_tabs(tabs_data)
    return tabs_data

if __name__ == "__main__":
    main()

