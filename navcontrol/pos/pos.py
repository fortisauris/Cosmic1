from flask import Flask

app = Flask()

POS = {'Zem':420, 'Slnko': 152000000, 'Mesiac':384000, 'Mars':67000000}  # vzdialenost v km


@app.route('/pos', methods=['GET']
def position():
    return f'Vzdialenosti Cosmic1 od { POS } v km.'
           
      
