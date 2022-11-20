from webscraper import app

# checks if the app.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
    # app.run(host="0.0.0.0", port=8080, threaded=True, debug=True)
