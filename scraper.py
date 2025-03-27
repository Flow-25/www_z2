import wikipedia
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import unicodedata
import re

def format_oven_name(name: str) -> str:
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')

def resize_imge(img_link):
    return img_link.replace("120px", "480px")
def get_first_image(query):
    try:
        page = wikipedia.page(query)
        img_link = page.images[0] if page.images else "No image found"
        return img_link
    except wikipedia.exceptions.PageError:
        return "Page not found"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation Error: {e.options[0]}"  # Picks first suggested page
    except Exception as e:
        return f"Error: {str(e)}"
def get_oven_list():
    file_path = "ovens_list.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)

    url = "https://en.wikipedia.org/wiki/List_of_ovens"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
    tables = table.find_all("tbody")

    cathegories = ["Earth Ovens", "Baking Ovens", "Industrial Ovens", "Kilns"]

    ovens = []
    i = 0
    for table in tables:
        rows = table.find_all("tr")
        cathegory = cathegories[i]
        i += 1
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 1:
                name = cells[0].text.replace("[dubious – discuss]", "").strip()
                wiki_link = cells[0].find("a")
                if wiki_link is not None:
                    query = wiki_link["href"]
                    wiki_link = "https://en.wikipedia.org" + wiki_link["href"]
                else:
                    wiki_link = "No link available"
                    query = ""

                img_link = cells[1].find("img", {"class": "mw-file-element"})
                if name == "Flame broiler":
                    img_link = cells[1].find_next("img", {"class": "mw-file-element"})
                if img_link is not None:
                    img_link = "https:" + img_link["src"]
                    img_link = resize_imge(img_link)
                else:
                    if name in ["Batch oven", "Clean process oven", "Reach-in oven", "Burn-in oven", "Spiral ovens", "Chorkor oven", "Kitchener range", "Kyoto box", "Rotimatic", "Self-cleaning oven", "Trivection oven"]:
                        img_link = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Factory.svg/502px-Factory.svg.png"
                    else:
                        img_link = get_first_image(name)
                
                ovens.append({"name": name, "wiki_link": wiki_link, "img_link": img_link, "cathegory": cathegory})
    df = pd.DataFrame(ovens)
    df.to_csv(file_path, index=False)
    return df
def gen_html_flashcard(data):
    name = data["name"].strip()
    img_link = data["img_link"].strip()
    cathegory = data["cathegory"]
    emoji = {
        "Earth Ovens": "🌍",
        "Baking Ovens": "🍞",
        "Industrial Ovens": "🏭",
        "Kilns": "🔥"
    }

    return f"""<a href="ovens/{format_oven_name(name)}.html" class="block">
    <div class="bg-white/20 p-4 rounded-xl shadow-md backdrop-blur-lg hover:scale-105 hover:bg-white/5 transition duration-300">
        <h2 class="text-2xl font-semibold">{emoji[cathegory]} {name}</h2>
        <img src="{img_link}" alt="{name}" class="w-full h-48 object-cover rounded-lg shadow-md">
    </div>
    </a>""".strip()
def create_flashcards(data):
    html = ""
    for i, row in data.iterrows():
        html += gen_html_flashcard(row.to_dict())
    return html

def create_cathegory_page(cathegory):
    df = get_oven_list()
    df = df[df["cathegory"] == cathegory]
    welcome_text = {
        "Earth Ovens":"Earth ovens are one of the oldest types of ovens, dating back thousands of years. \nThese traditional ovens are made by digging pits in the ground and heating them with fire. \nThey are commonly used for slow-cooking food and remain popular in traditional cooking around the world.",
        "Baking Ovens":"Baking ovens are used for baking bread, cakes, and other baked goods. \nThey are heated by gas, electricity, or wood, and can be found in homes, bakeries, and restaurants. \nBaking ovens come in many shapes and sizes, from small countertop models to large commercial ovens.",
        "Industrial Ovens":"Industrial ovens are used in a variety of industries, including food processing, automotive manufacturing, and electronics production. \nThese ovens are designed for high-volume production and can reach high temperatures for fast and efficient cooking or curing. \nIndustrial ovens come in many different types, including conveyor ovens, batch ovens, and tunnel ovens.",
        "Kilns":"Kilns are used for firing ceramics, glass, and other materials at high temperatures. \nThey are commonly used in pottery studios, glassblowing workshops, and industrial manufacturing plants. \nKilns come in many different shapes and sizes, from small tabletop models to large industrial kilns."
    }
    file_names = {
        "Earth Ovens": "earth",
        "Baking Ovens": "baking",
        "Industrial Ovens": "industrial",
        "Kilns": "kilns"
    }
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smoking Ovens</title>
        <link href="../output.css" rel="stylesheet">
    </head>
    <body style="background-image: url('backgrounds/{file_names[cathegory]}_bg.jpg');" class="bg-center bg-cover bg-fixed min-h-screen text-white">

    <!-- Go Back Button -->
    <div class="absolute top-6 left-6 md:block hidden">
        <button onclick="history.back()" 
            class="relative px-6 py-3 text-lg font-bold uppercase tracking-wide 
                   rounded-full bg-gradient-to-r from-gray-300 to-gray-500 dark:from-gray-600 dark:to-gray-800 
                   shadow-lg text-black dark:text-white transition-all duration-300 ease-in-out 
                   hover:scale-105 hover:shadow-gray-400/80 dark:hover:shadow-gray-300/50 
                   before:absolute before:inset-0 before:bg-gray-400/20 dark:before:bg-gray-700/30 
                   before:rounded-full before:blur-lg before:transition-all before:duration-300 before:ease-in-out 
                   hover:before:opacity-100">
            ⬅️ Go Back
        </button>
    </div>


        <!-- Header -->
        <div class="container mx-auto py-10 text-center">
            <h1 class="text-5xl font-bold text-white">{cathegory}</h1>
            <p class="mt-6 text-lg max-w-3xl mx-auto text-gray-200">
            {welcome_text[cathegory]}
            </p>
        </div>

        <!-- Flashcards Section -->
        <div class="container mx-auto mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            {create_flashcards(df)}
        </div> 
    </body>
    </html>
        """

    with open(f"cathegories/{file_names[cathegory]}.html", "w") as file:
        file.write(html)

def create_oven_page(oven, df):
    name = oven["name"]
    img_link = oven["img_link"]
    wiki_link = oven["wiki_link"]
    cathegory = oven["cathegory"]
    emoji = {
        "Earth Ovens": "🌍",
        "Baking Ovens": "🍞",
        "Industrial Ovens": "🏭",
        "Kilns": "🔥"
    }

    try:
        if name == "Kalua":
            summary = wikipedia.summary("Kalua (cooking)")
        elif name == "Cooker":
            summary = wikipedia.summary("Pressure Cooker")
        elif name == "Pachamanca":
            summary = wikipedia.summary("Pachamanca (Quechua)")
        elif name == "Tannur":
            summary = wikipedia.summary("Clay oven")
        else:
            summary = wikipedia.summary(name)
    except Exception:
        return
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{name} - {cathegory}</title>
        <link href="../../output.css" rel="stylesheet">
    </head>
    <body class="bg-white text-black dark:bg-[#121212] dark:text-white min-h-screen flex flex-col items-center justify-center">

    <!-- Go Back Button -->
    <div class="absolute top-6 left-6 md:block hidden">
        <button onclick="history.back()" 
            class="relative px-6 py-3 text-lg font-bold uppercase tracking-wide 
                   rounded-full bg-gradient-to-r from-gray-300 to-gray-500 dark:from-gray-600 dark:to-gray-800 
                   shadow-lg text-black dark:text-white transition-all duration-300 ease-in-out 
                   hover:scale-105 hover:shadow-gray-400/80 dark:hover:shadow-gray-300/50 
                   before:absolute before:inset-0 before:bg-gray-400/20 dark:before:bg-gray-700/30 
                   before:rounded-full before:blur-lg before:transition-all before:duration-300 before:ease-in-out 
                   hover:before:opacity-100">
            ⬅️ Go Back
        </button>
    </div>

    <!-- Content Container -->
    <div class="container mx-auto px-6 py-12 text-center">
        <!-- Title -->
            <h1 class="text-6xl font-extrabold text-black dark:text-white">
                {name}
            </h1>

        <!-- Image -->
        <div class="mt-8">
            <img src="{img_link}" 
                 alt="{name}" class="w-full max-w-2xl mx-auto rounded-2xl shadow-xl border-4 border-gray-300 dark:border-gray-800">
        </div>

        <!-- Summary Box -->
        <div class="mt-8 bg-gray-200/40 dark:bg-gray-800/40 p-6 rounded-lg shadow-lg max-w-3xl mx-auto">
            <p class="text-lg text-gray-800 dark:text-gray-300 leading-relaxed">
                {summary}
            </p>
        </div>

        <!-- Wikipedia Link -->
        <div class="mt-6 flex justify-center">
            <a href="{wiki_link}" target="_blank">
                <div class="mt-8">
                    <div class="relative px-6 py-5 bg-blue-600 mx-auto bg-gradient-to-r from-blue-500 to-indigo-600 
                    text-white text-lg font-bold rounded-full shadow-lg transition-all duration-300 hover:scale-105 
                    hover:shadow-blue-400/80">
                
                    <!-- Pulsing Dot -->
                    <span class="absolute top-0 right-0 mt-1 mr-1 flex h-3 w-3">
                        <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-400 opacity-75"></span>
                        <span class="relative inline-flex h-3 w-3 rounded-full bg-sky-500"></span>
                    </span>
                    <p>
                        📖 Read More on Wikipedia
                    </p>
                </div>
             </a>
        </div>
    </div>

    </body>
    </html>
    """

    filename = format_oven_name(name)+".html"
    with open(f"cathegories/ovens/{filename}", "w") as file:
        file.write(html)

def create_oven_pages():
    df = get_oven_list()
    for i, row in df.iterrows():
        create_oven_page(row.to_dict(), df)
        print(f"Page {i+1}/{len(df)} created")
if __name__ == '__main__':
    create_cathegory_page("Earth Ovens")
    create_cathegory_page("Baking Ovens")
    create_cathegory_page("Industrial Ovens")
    create_cathegory_page("Kilns")
    create_oven_pages()