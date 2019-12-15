import requests
from bs4 import BeautifulSoup

response = requests.get('http://reslife.umd.edu/hallsatglance/')

soup = BeautifulSoup(response.text, features="html.parser")

lists = soup.find_all("td", {"width" : "62"})
cutoff = lists[1:]

# lambda tag:tag.name=="tr"

cutoff = list(filter(lambda tag:tag.get_text()!="", cutoff))

print(len(cutoff))

for list in cutoff:
    print(list.get_text())
