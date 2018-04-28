from flask import Flask, jsonify, request
from flask_cors import CORS
from pymodm import connect
import models
import datetime
import numpy as np

connect("mongodb://localhost:27017/pod_annotate")
app = Flask(__name__)
CORS(app)


@app.route("/api/get_pods", methods=["GET"])
def get_pods():
    podcasts = []
    pods = models.NotedMedia.objects.all()
    for pod in pods:
        podcasts.append(pod.media_title)
    data = {
        "success": 1,
        "podcasts": podcasts
    }
    return jsonify(data), 200

@app.route("/api/add_note", methods=["POST"])
def add_note():
    """
    Stores heart rate measurement for user with this email
    :param user_email: email (string) of user (POST param)
    :param heart_rate: heart rate (float/int) of user (POST param)
    :param user_age: user age (float/int) (POST param)
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    """
    r = request.get_json()
    print('expected JSON here')
    print(r)
    print(request)
    ts_now = datetime.datetime.now()
    # if(is_email_valid(r["user_email"]) is not True):
    #     data = {
    #         "success": 0,
    #         "error_message": "invalid email"
    #     }
    #     return jsonify(data), 400
    #
    # if(is_int_or_float(r["heart_rate"]) is not True):
    #     data = {
    #         "success": 0,
    #         "error_message": "invalid heart_rate. Expects float or int."
    #     }
    #     return jsonify(data), 400
    #
    # if(is_int_or_float(r["user_age"]) is not True):
    #     data = {
    #         "success": 0,
    #         "error_message": "invalid age. Expects float or int."
    #     }
    #     return jsonify(data), 400

    if(does_pod_exist(r["media_id"])):
        add_note_to_media(r["media_id"], r["ts_start"], r["ts_end"], r["body"],
                          ts_now)
    else:
        create_noted_media(r["media_id"], r["media_src"], r["media_title"],
                           r["media_img"], r["ts_start"], r["ts_end"],
                           r["body"], ts_now)

    data = {"success": 1}
    return jsonify(data), 200


@app.route("/api/get_notes/", methods=["POST"])
def get_notes():
    """
    Returns all heart rate readings for specified user
    :params user_email: user email (GET param)
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    :returns user_data.email: users email (when status = 200)
    :returns user_data.age: user age (when status = 200)
    :returns user_data.hr_reading: user heart rate readings (when status = 200)
    :returns user_data.readings_ts: ts of reading inserts (when status = 200)
    """
    r = request.get_json()
    media_id = r["media_id"]
    if(does_pod_exist(media_id)):
        nm = models.NotedMedia.objects.raw({"_id": media_id}).first()
        pod_data = {
            "media_id": nm.media_id,
            "media_src": nm.media_src,
            "media_title": nm.media_title,
            "media_img": nm.media_img,
            "ts_start": nm.ts_start,
            "ts_end": nm.ts_end,
            "body": nm.body,
            "ts_insert": nm.ts_insert
        }
        response_data = {
            "status": 1,
            "media_data": pod_data
        }
    else:
        response_data = {
            "status": 0,
            "error_message": media_id + " has no stored notes"
        }

    return jsonify(response_data), 200

@app.route("/api/delete_note", methods=["POST"])
def delete_note():
    """
    Returns all heart rate readings for specified user
    :params user_email: user email (GET param)
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    :returns user_data.email: users email (when status = 200)
    :returns user_data.age: user age (when status = 200)
    :returns user_data.hr_reading: user heart rate readings (when status = 200)
    :returns user_data.readings_ts: ts of reading inserts (when status = 200)
    """
    r = request.get_json()
    media_id = r["media_id"]
    ts_start = r["ts_start"]
    if(does_pod_exist(media_id)):
        nm = models.NotedMedia.objects.raw({"_id": media_id}).first()
        index_of_note = nm.ts_start.index(float(ts_start))
        del nm.ts_start[index_of_note]
        del nm.ts_end[index_of_note]
        del nm.body[index_of_note]
        del nm.ts_insert[index_of_note]
        nm.save()
        response_data = {
            "status": 1,
            "message": "note deleted"
        }
    else:
        response_data = {
            "status": 0,
            "error_message": media_id + " has no stored notes"
        }

    return jsonify(response_data), 200


def does_pod_exist(media_id):
    """
    Returns whether user exists in Mongo
    :params email: user email
    :returns True/False: boolean
    """
    print('this is the media_id: ')
    print(media_id)
    try:
        nm = models.NotedMedia.objects.raw({"_id": media_id}).first()
        return(True)
    except:
        return(False)


def is_int_or_float(val):
    """
    Returns whether val is int/float
    :params val: value to test
    :returns True/False: boolean
    """
    if(isinstance(val, int) or isinstance(val, float)):
        return(True)
    else:
        return(False)


def create_noted_media(media_id, media_src, media_title, media_img, ts_start, ts_end, body, ts_now):
    """
    Creates a user with the specified email and age. If the user already exists
    in the DB this WILL overwrite that user. It also adds the specified
    heart_rate to the user
    :param email: str email of the new user
    :param age: number age of the new user
    :param heart_rate: number initial heart_rate of this new user
    :param time: datetime of the initial heart rate measurement
    """
    nm = models.NotedMedia(media_id, media_src, media_title, media_img, [], [], [], [])  # create a new User instance
    nm.ts_start.append(ts_start)  # add initial heart rate
    nm.ts_end.append(ts_end)
    nm.body.append(body)
    nm.ts_insert.append(ts_now)
    nm.save()  # save the user to the database


def add_note_to_media(media_id, ts_start, ts_end, body, ts_insert):
    """
    Appends a heart_rate measurement at a specified time to the user specified
    by email. It is assumed that the user specified by email exists already.
    :param email: str email of the user
    :param heart_rate: number heart_rate measurement of the user
    :param time: the datetime of the heart_rate measurement
    """
    nm = models.NotedMedia.objects.raw({"_id": media_id}).first()
    nm.ts_start.append(ts_start)
    nm.ts_end.append(ts_end)
    nm.body.append(body)
    nm.ts_insert.append(ts_insert)
    nm.save()
