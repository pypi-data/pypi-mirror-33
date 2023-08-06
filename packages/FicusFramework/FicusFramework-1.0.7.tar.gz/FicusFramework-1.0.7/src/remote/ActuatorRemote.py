from flask import jsonify

from . import remote


@remote.route('/actuator/info', methods=['GET'])
def actuator_info():
    return jsonify({})


@remote.route('/actuator/health', methods=['GET'])
def actuator_health():
    return jsonify({"status": "UP"})
