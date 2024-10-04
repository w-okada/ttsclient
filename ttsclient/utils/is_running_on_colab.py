import os


def is_running_on_colab():

    return "COLAB_GPU" in os.environ
