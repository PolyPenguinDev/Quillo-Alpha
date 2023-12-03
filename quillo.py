#!/usr/bin/env python
import argparse
import requests
from bs4 import BeautifulSoup
import os
import re
import json
import html2text
h = html2text.HTML2Text()
bolde = {"A":"𝗔","B":"𝗕","C":"𝗖","D":"𝗗","E":"𝗘","F":"𝗙","G":"𝗚", "H":"𝗛", "I":"𝗜","J":"𝗝","K":"𝗞","L":"𝗟","M":"𝗠","N":"𝗡","O":"𝗢","P":"𝗣","Q":"𝗤","R":"𝗥","S":"𝗦","T":"𝗧","U":"𝗨","V":"𝗩","W":"𝗪","X":"𝗫","Y":"𝗬","Z":"𝗭","a":"𝗮","b":"𝗯","c":"𝗰","d":"𝗱","e":"𝗲","f":"𝗳","g":"𝗴","h":"𝗵","i":"𝗶","j":"𝗷","k":"𝗸","l":"𝗹","m":"𝗺","n":"𝗻","o":"𝗼","p":"𝗽","q":"𝗾","r":"𝗿","s":"𝘀","t":"𝘁","u":"𝘂","v":"𝘃","w":"𝘄","x":"𝘅","y":"𝘆","z":"𝘇","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵", "0":"𝟬"}
h.ignore_links = False
def bold(text):
    line = ""
    for i in text.split("\n"):
        ins = 0
        isbold=True
        linez = True
        t=""
        for j in i:
            if isbold:
                if ins == 2:
                    if j != "#":
                        linez= False
                elif ins <= 1:
                    isbold = j == "#"
                    linez = linez and isbold
                    if j != "#":
                        t+=j
                else:
                    try:
                        t+=bolde[j]
                    except:
                        t+=j
            else:
                t+=j
            ins +=1
        if line != "":
            line += "\n"+t
            if linez and len(t) > 2:
                line += "\n───────────────────────────────────────────────────────────────────"

        else:
            line = t
    return line
        

def replace_bullets_with_symbol(markdown_text, symbol='•'):
    pattern = r'^\s*[-*+]'
    return re.sub(pattern, symbol, markdown_text, flags=re.MULTILINE)

def replace_links(markdown):
    link_pattern = re.compile(r'\[([^]]+)\]\(([^)]+)\)')
    matches = link_pattern.findall(markdown)
    link_list = [[] for _ in range(len(matches))]

    for i, (text, link) in enumerate(matches, start=1):
        reference = f'{text} [{i}]'
        link_list[i-1].append(link)
        markdown = link_pattern.sub(reference, markdown, 1)

    return markdown, link_list

def remove_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(['style', 'script', 'img']):
        data.decompose()
    return soup.prettify()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    parser = argparse.ArgumentParser(description="A simple command-line program.")
    parser.add_argument("site", help="The website to view.")
    parser.add_argument("-o", "--open", action="store_true", help="Opens a website in a new tab.")
    parser.add_argument("-t", "--tab", action="store_true", help="Switches tab.")
    parser.add_argument("-f", "--format", action="store_true", help="Formats HTML into a more readable format")
    parser.add_argument("-g", "--go", action="store_true", help="Switches the current tab to a new website.")
    parser.add_argument("-s", "--search", action="store_true", help="Searches something on google.")
    parser.add_argument("-c", "--close", action="store_true", help="closes a tab.")

    args = parser.parse_args()

    if args.open or args.go:
        clear_console()
        try:
            int(args.site)
            with open('tabs.json', 'r') as f:
                l = json.load(f)
            args.site = l["tabs"][l["current"]-1]["links"][int(args.site)-1][0]
        except:
            args.site = f"http://www.{args.site}" if not args.site.startswith('http') else args.site
        print(f"Loading {args.site} ...")
        response = requests.get(args.site)
        soup = BeautifulSoup(response.content, 'html.parser')
        out = remove_tags(soup.prettify())
        if args.format:
            title = soup.title.text.strip()
            clear_console()
            print(f"\n---------⃝🖋️ Quillo Text-Based Browser---------")
            with open('tabs.json', 'r') as f:
                l = json.load(f)
            job_elements = soup.find_all()
            out = replace_bullets_with_symbol(h.handle(out))
            out2 = bold(replace_links(out)[0])
            if args.open:
                l["tabs"].append({"title": title, "links":replace_links(out)[1], "content":out2})
                l["current"] = len(l["tabs"])
            else:
                l["tabs"][l["current"]-1]={"title": title, "links":replace_links(out)[1], "content":out2}
            n = 0
            s = "|"
            for i in l["tabs"]:
                n+=1
                s+=" "+str(n)+". "+i["title"]+" |"
            for i in range(len(s)):
                    print("─", end = "")
            print()
            print(s)
            for i in range(len(s)):
                    print("─", end = "")
            print("\n")
            print(out2)
            with open('tabs.json', 'w') as f:
                json.dump(l, f)
    elif args.tab:
        clear_console()
        print(f"\n---------⃝🖋️ Quillo Text-Based Browser---------")
        with open('tabs.json', 'r') as f:
            l = json.load(f)
        n = 0
        s = "|"
        for i in l["tabs"]:
            n+=1
            s+=" "+str(n)+". "+i["title"]+" |"
        for i in range(len(s)):
            print("─", end = "")
        print()
        print(s)
        for i in range(len(s)):
                print("─", end = "")
        print("\n")
        print(l["tabs"][int(args.site)-1]["content"])
        l["current"]=int(args.site)-1
        with open('tabs.json', 'w') as f:
            json.dump(l, f)
    elif args.search:
        clear_console()
        args.site = f"http://www.google.com/search?q={args.site}"
        print(f"Loading {args.site} ...")
        response = requests.get(args.site)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.text.strip()
        clear_console()
        print(f"\n---------⃝🖋️ Quillo Text-Based Browser---------")
        with open('tabs.json', 'r') as f:
            l = json.load(f)
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
                    content += f"{text_content} [{str(len(links)+1)}]"
                    links.append(["https://www.google.com/"+link_text])
                except:
                    pass
        l["tabs"].append({"title":title, "content":content, "links" : links})
        n = 0
        s = "|"
        for i in l["tabs"]:
            n+=1
            s+=" "+str(n)+". "+i["title"]+" |"
        for i in range(len(s)):
            print("─", end = "")
        print()
        print(s)
        for i in range(len(s)):
                print("─", end = "")
        print("\n")
        print(content)
        with open('tabs.json', 'w') as f:
            json.dump(l, f)
    elif args.close:
        with open('tabs.json', 'r') as f:
            l = json.load(f)
        if int(args.site) < l["current"]:
            l["current"] -= 1
        l["tabs"].pop(int(args.site)-1)
        with open('tabs.json', 'w') as f:
            json.dump(l, f)
        args.site = str(l["current"])
        clear_console()
        print(f"\n---------⃝🖋️ Quillo Text-Based Browser---------")
        with open('tabs.json', 'r') as f:
            l = json.load(f)
        n = 0
        s = "|"
        for i in l["tabs"]:
            n+=1
            s+=" "+str(n)+". "+i["title"]+" |"
        for i in range(len(s)):
            print("─", end = "")
        print()
        print(s)
        for i in range(len(s)):
                print("─", end = "")
        print("\n")
        print(l["tabs"][int(args.site)-1]["content"])
        l["current"]=int(args.site)-1
        with open('tabs.json', 'w') as f:
            json.dump(l, f)
        

if __name__ == "__main__":
    main()
