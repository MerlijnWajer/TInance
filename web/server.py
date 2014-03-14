from flask import Flask, request, abort, render_template
app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET'])
def main():
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0')
