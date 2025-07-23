from app import app

# This block is for running the app locally with PyCharm Community Edition
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
