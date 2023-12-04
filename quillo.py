#!/usr/bin/env python
import click
import requests
import builtins
from bs4 import BeautifulSoup
import os
import re
import json
import html2text

# Define global constant
TAB_FILE = "C:\\Users\\caleb\\OneDrive\\Documents\\Quillo\\tabs.json"

CIRCLE_MAP = {"1": "❶", "2": "❷", "3": "❸", "4": "❹", "5": "❺", "6": "❻", "7": "❼", "8": "❽", "9": "❾", "0": "⓿"}
UB_CIRCLE_MAP = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦", "8": "⑧", "9": "⑨", "0": "⓪"}
# Initialize HTML to Text converter
html_to_text = html2text.HTML2Text()
html_to_text.ignore_links = False
file = builtins.open

def newtabd():
    return """     _
 ╭──╱ |    ___       _ _ _     
 | ╱ ╱ |  / _ \ _  _(_) | |___ 
 |╱╱   | ▕ (_) | || | | | / _ \\
 ▀─────╯  \__\_\\\\_,_|_|_|_\___/
 NEW TAB
Use \033[1m\033[3mquillo -s "query"\033[0m to search google
Use \033[1m\033[3mquillo -f -o "URL"\033[0m to open a website in a new tab.
Use \033[1m\033[3mquillo -f -g "URL"\033[0m to open a website in a this tab.
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
            t = "\033[1m" + t + "\033[0m"
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


def replace_links(markdown, url_start):
    """
    Replace links in the markdown text and extract them for future reference.
    """
    link_pattern = re.compile(r'\[([^]]+)\]\(([^)]+)\)')
    matches = link_pattern.findall(markdown)
    link_list = [[] for _ in range(len(matches))]

    for i, (text, link) in enumerate(matches, start=1):
        reference = f'{text} [{i}]'
        if link.startswith("/"):
            link_list[i - 1].append(url_start+link)
        else:
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
    with file(TAB_FILE, 'r') as f:
        return json.load(f)


def save_tabs(tabs_data):
    """
    Save tabs data to the file.
    """
    for i in tabs_data["overrides"]:
        if i.startswith("clear"):
            tabs_data["clear"]= not tabs_data["clear"]
        if i.startswith("format"):
            tabs_data["format"]= not tabs_data["format"]
    del tabs_data["overrides"]

    with file(TAB_FILE, 'w') as f:
        json.dump(tabs_data, f)


@click.command()
@click.option("-o", "--open", type=str, help="Opens a website in a new tab.")
@click.option("-t", "--tab", type = int, help="Switches tab.")
@click.option("-f", "--format", is_flag=True, help="Formats HTML into a more readable format")
@click.option("-g", "--go", type=str, help="Switches the current tab to a new website.")
@click.option("-s", "--search", type=str, help="Searches something on google.")
@click.option("-c", "--close", type=int, help="closes a tab.")
@click.option("-a", "--advanced", type=str, help="changes advanced settings.")
@click.option("-v", "--overrides", type=str, help="overrides advanced settings.")
@click.option("-n", "--newtab", is_flag=True, help="Opens a new tab")
def main(open, tab, format, go, search, close, advanced, newtab, overrides):
    # Command-line argument parsing
    tabs_data = load_tabs()
    tabs_data.update({"overrides":[]})
    if overrides:
        tabs_data["overrides"] = overrides.split(", ")
        for i in overrides.split(", "):
            if i.startswith("clear"):
                if tabs_data["clear"] == "true" in i.lower():
                    tabs_data["overrides"].remove(i)
                else:
                    tabs_data["clear"] = "true" in i.lower()
            if i.startswith("format"):
                if tabs_data["format"] == "true" in i.lower():
                    tabs_data["overrides"].remove(i)
                else:
                    tabs_data["format"] = "true" in i.lower()
    with file(TAB_FILE, 'w') as f:
        json.dump(tabs_data, f)
    format = format ^ tabs_data["format"]
    if open or go:
        site = go
        if open:
            site=open
        clear_console()
        if site.isdigit():
            site = tabs_data["tabs"][tabs_data["current"] - 1]["links"][int(site) - 1][0]
        else:
            site = f"http://www.{site}" if not site.startswith('http') else site
        host = "https://"+site.split("/")[2]
        print(f"Loading {site} ...")
        response = requests.get(site)
        site = response.url
        soup = BeautifulSoup(response.content, 'html.parser')
        formatted_html = remove_tags(soup.prettify())
        if format:
            title = soup.title.text.strip()
            clear_console()
            formatted_html = replace_bullets_with_symbol(html_to_text.handle(formatted_html))
            formatted_html_old = formatted_html
            formatted_html = boldify(replace_links(formatted_html, host)[0])
        else:
            title = soup.title.text.strip()
            clear_console()
            formatted_html = soup.prettify()
        if open:
            if format:
                tabs_data["tabs"].append({"title": title, "links": replace_links(formatted_html, host)[1], "content": formatted_html})
            else:
                tabs_data["tabs"].append({"title": title, "links": [], "content": formatted_html})
            tabs_data["current"] = len(tabs_data["tabs"])
        else:
            if format:
                tabs_data["tabs"][tabs_data["current"] - 1] = {"title": title, "links": replace_links(formatted_html_old, host)[1], "content": formatted_html}
            else:
                tabs_data["tabs"][tabs_data["current"] - 1] = {"title": title, "links": [], "content": formatted_html}
        print_tabs(tabs_data)
        save_tabs(tabs_data)
    elif tab:
        clear_console()
        tabs_data["current"] = tab
        print_tabs(tabs_data)
        save_tabs(tabs_data)
    elif search:
        clear_console()
        site = f"http://www.google.com/search?q={search}"
        print(f"Loading {site} ...")
        response = requests.get(site)
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
                    if not ["https://www.google.com/" + link_text] in links:
                        soupp = BeautifulSoup(a_tag.prettify(), 'html.parser')
                        text_content = soupp.find('h3', class_='zBAuLc l97dzf').div.text
                        content += f"{text_content} [{str(len(links) + 1)}]"
                        links.append(["https://www.google.com/" + link_text])
                except:
                    pass
        tabs_data["tabs"].append({"title": title, "content": content, "links": links})
        tabs_data["current"] = len(tabs_data["tabs"])
        print_tabs(tabs_data)
        save_tabs(tabs_data)
    elif close:
        tabs_data = close_tab(tabs_data, close)
        save_tabs(tabs_data)
    elif advanced:
        e = load_tabs()
        if advanced == "help":
            print(f"""How to use Quillo -a
                  
Usage: \033[1m\033[3mquillo -a SETTING=VALUE\033[0m
                  
Settings:
    •\033[1m\033[3mclear\033[0m - clear the console when running commands. Current value: \033[1m\033[3m{str(e["clear"])}\033[0m
    •\033[1m\033[3mformat\033[0m - make it so you don't need to do -f every time. Current value:a \033[1m\033[3m{str(e["format"])}\033[0m""")
    
        elif advanced.startswith("clear="):
            e["clear"] = "true" in advanced.lower()
            save_tabs(e)
        elif advanced.startswith("format="):
            e = load_tabs()
            e["format"] = "true" in advanced.lower()
            save_tabs(e)
    elif newtab:
        clear_console()
        tabs_data["tabs"].append({"title": "New Tab", "content": newtabd()})
        tabs_data["current"] = len(tabs_data["tabs"])
        print_tabs(tabs_data)
        save_tabs(tabs_data)
    else:
        clear_console()
        print_tabs(tabs_data)


def print_tabs(tabs_data):
    """
    Print the tabs data to the console.
    """
    print(f"\n---------⃝🖋️ Quillo Text-Based Browser v1.0-B1---------")
    n = 0
    s = "|"
    for tab in tabs_data["tabs"]:
        n += 1
        p = str(n)
        if n == tabs_data["current"]:
            p2 = ""
            for i in p:
                p2 += CIRCLE_MAP[i]
            p = p2
        else:
            p2 = ""
            for i in p:
                p2 += UB_CIRCLE_MAP[i]
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
    if tabs_data["current"] == 0:
        tabs_data["current"] = 1
    tabs_data["tabs"].pop(tab_index - 1)
    clear_console()
    if len(tabs_data["tabs"]) == 0:
        tabs_data["tabs"].append({"title": "New Tab", "content": newtabd()})
    print_tabs(tabs_data)
    return tabs_data


if __name__ == "__main__":
    main()