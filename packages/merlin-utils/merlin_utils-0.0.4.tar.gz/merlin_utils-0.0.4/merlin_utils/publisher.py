import base64

from apiclient import discovery
# default; set to your traffic topic. Can override on command line.
from oauth2client.client import GoogleCredentials

TRAFFIC_TOPIC = 'projects/{}/topics/{}'

PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']

NUM_RETRIES = 3


class Publisher():
    _client = None
    _project = None
    _topic = None

    def __init__(self, project, topic=None, credentials=None):
        if not isinstance(project, str):
            raise Exception("Project must be a string")
        if topic and not isinstance(topic, str):
            raise Exception("topic must be a string")
        self._client = self.create_pubsub_client(credentials)
        self._project = project
        self._topic = topic

    @classmethod
    def create_pubsub_client(cls, credentials):
        """Build the pubsub client."""
        if not credentials:
            credentials = GoogleCredentials.get_application_default()
            if credentials.create_scoped_required():
                credentials = credentials.create_scoped(PUBSUB_SCOPES)
        return discovery.build('pubsub', 'v1beta2', credentials=credentials)

    def publish(cls, msg, pubsub_topic=None, msg_attributes=None):

        if cls._client is None:
            raise Exception("Class not instantiated\n"
                            "Please make sure to call Publish(project='project')")

        if not pubsub_topic and not cls._topic:
            raise Exception("Topic must be instanciated")

        if pubsub_topic:
            pubsub_topic = TRAFFIC_TOPIC.format(cls._project, pubsub_topic)
        else:
            pubsub_topic = TRAFFIC_TOPIC.format(cls._project, cls._topic)

        data = base64.b64encode(msg)
        msg_payload = {'data': data.decode("utf-8")}
        if msg_attributes:
            msg_payload['attributes'] = msg_attributes
        body = {'messages': [msg_payload]}
        resp = cls._client.projects().topics().publish(
            topic=pubsub_topic, body=body).execute(num_retries=NUM_RETRIES)
        return resp
