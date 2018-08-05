#!/usr/bin/python3
# -*- coding:utf8 -*-
import json
from flask import Flask, request, make_response, jsonify

app = Flask("My-Local-Traffic-Planner")

def respond(fullfilment):
    return make_response(jsonify({'fulfillmentText': fullfilment}))


@app.route('/departures', methods=['POST'])
def departures_handler():
    try:
        req = request.get_json(silent=True, force=True)
        print(json.dumps(req))

        location = req.get('queryResult').get('parameters').get('current-location')

        if location == 'home':
            return respond("Oh so you are home now. Well, you better hurry!")
        elif location == 'work':
            return respond("At work? Well, are you sure it's time to leave already?")
        else:
            return respond("I am not sure where " + location + " is.")

    except Exception as e:
        print(e)
        return respond("Sorry, an error occurred. Please check the server logs.")


def main():
    app.run()


if __name__ == '__main__':
    main()
