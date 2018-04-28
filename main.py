from pymodm import connect
import models
import datetime


def add_note(media_id, ts_start, ts_end, body):
    """
    Appends a heart_rate measurement at a specified time to the user specified
    by email. It is assumed that the user specified by email exists already.
    :param email: str email of the user
    :param heart_rate: number heart_rate measurement of the user
    :param time: the datetime of the heart_rate measurement
    """
    # Get the first user where _id=email:
    nm = models.NotedMedia.objects.raw({"_id": media_id}).first()
    # Append the heart_rate to the user's list of heart rates:
    nm.ts_start.append(ts_start)
    # append the current time to the user's list of heart rate times:
    nm.ts_end.append(ts_end)
    # save the user to the database
    nm.body.append(body)
    nm.ts_insert.append(datetime.datetime.now())
    nm.save()


def create_noted_media(media_id, media_src, email, ts_start, ts_end, body):
    """
    Creates a user with the specified email and age. If the user already exists
    in the DB this WILL overwrite that user. It also adds the specified
    heart_rate to the user
    :param email: str email of the new user
    :param age: number age of the new user
    :param heart_rate: number initial heart_rate of this new user
    :param time: datetime of the initial heart rate measurement
    """
    nm = models.NotedMedia(media_id, media_src, email, [], [], [], [])  # create a new User instance
    nm.ts_start.append(ts_start)  # add initial heart rate
    nm.ts_end.append(ts_end)  # add initial heart rate time
    nm.body.append(body)
    nm.ts_insert.append(datetime.datetime.now())
    nm.save()  # save the user to the database


def print_noted_media(media_id):
    """
    Prints the user with the specified email
    :param email: str email of the user of interest
    :return:
    """
    nm = models.NotedMedia.objects.raw({"_id": media_id}).first()
    print(nm)
    print(nm.media_id)
    print(nm.media_src)
    print(nm.email)
    print(nm.ts_start)
    print(nm.ts_end)
    print(nm.body)

if __name__ == "__main__":
    connect("mongodb://localhost:27017/pod_annotate")
    # create_noted_media(media_id="pod1",
    #                    media_src="https://pod.net",
    #                    email="test@test.com",
    #                    ts_start="10.2",
    #                    ts_end="14.4",
    #                    body="this is the first annotated note.")
    add_note(media_id="pod1", ts_start="124.7", ts_end="140.876", body="note numero dos")
    print_noted_media("pod1")
