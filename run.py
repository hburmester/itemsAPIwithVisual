from api_connect.app import app as api
from displaying.app import app as visual

if __name__ == '__main__':
    #api.run(port=5000, debug=True)
    visual.run(port=5001, debug=False)