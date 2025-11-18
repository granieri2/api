from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def estrai_eventi(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    eventi = []

    # Ogni blocco evento
    blocchi = soup.find_all("div", class_="blog-post-list")

    for blocco in blocchi:
        # Link alla pagina evento (se presente)
        link_tag = blocco.find_parent("a")
        link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None

        # Immagine (se presente)
        img_tag = blocco.find("img")
        img = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

        # Span interni (data, luogo, titolo)
        spans = blocco.find_all("span")
        spans_text = [s.get_text(strip=True) for s in spans]

        evento = {
            "data": spans_text[0] if len(spans_text) > 0 else None,
            "luogo": spans_text[1] if len(spans_text) > 1 else None,
            "titolo": spans_text[2] if len(spans_text) > 2 else None,
            "img": img,
            "link": link
        }

        eventi.append(evento)

    return eventi


@app.route("/estrai", methods=["GET"])
def estrai_route():
    url = request.args.get("url")

    if not url:
        return jsonify({"errore": "Devi passare un parametro ?url=..."}), 400

    try:
        risultati = estrai_eventi(url)
        return jsonify({"url": url, "eventi": risultati})

    except Exception as e:
        return jsonify({"errore": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
