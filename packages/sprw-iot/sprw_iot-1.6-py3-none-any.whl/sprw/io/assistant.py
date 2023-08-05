import datetime
import boto3
import json
import requests
from contextlib import closing
from pprint import pprint
import time
import pygame
from random import randint
import sys
import threading

import parsedatetime
from pytz import timezone
from requests_futures.sessions import FuturesSession

from sprw.io import speech_recognition
from .config import Config
from easydict import EasyDict as edict
from .exceptions import AuthenticationError, ValidationError, NetworkError, ServerError, Error, SpeechRecognitionError, UnknownValueError, WaitTimeoutError, RequestError, QuotaLimitReachedError


class Assistant:

    """Used for Home Assistant functionalities.

    Using the access token generated in the SPRW IoT Dashboard, the class can be instantiated.

    Example:
        The following example shows how to instantiate this class::

            from sprw.io import Assistant
            ACCESS_TOKEN = '<your-access-token>'
            assistant = Assistant(ACCESS_TOKEN)

    Attributes:
        access_token (int): Access token used to communincate with the SPRW IoT Server.
        microphone (sprw.io.speech_recognition.Microphone): Instance of the Microphone class. Available only when microphone is connected.
    """

    __aws_credentials = None
    __google_cloud_credentials = None
    __datetime_format = None
    __polly_client = None
    __initialised_assistant = False
    __voices = None

    __headers = None
    __number_in_words = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                         "Seventeen", "Eighteen", "Nineteen", "Twenty", "Twenty one",
                         "Twenty two", "Twenty three", "Twenty four", "Twenty five",
                         "Twenty six", "Twenty seven", "Twenty eight", "Twenty nine", "Thirty",
                         "Thirty one", "Thirty two", "Thirty three", "Thirty four", "Thirty five", "Thirty six",  "Thirty seven",
                         "Thirty eight", "Thirty nine", "Fourty", "Fourty one", "Fourty two", "Fourty three", "Fourty four", "Fourty five", "Fourty six", "Fourty seven",
                         "Fourty eight", "Fourty nine", "Fifty", "Fifty one", "Fifty two", "Fifty three", "Fifty four", "Fifty five", "Fifty six", "Fifty seven", "Fifty eight", "Fifty nine"
                         ]
    __month_in_words = ['January', 'February', 'March', 'April', 'May',
                        'June', 'July', 'August', 'September',
                        'October', 'Novemeber', 'December'
                        ]

    __network_error_message = 'Please check your internet connection. Could not connect with ' + Config.APP_URL
    __server_error_message = 'SPRW Server Error'
    __generic_error_message = 'Failed to communicate with the server'
    __authentication_error_message = 'Unauthenticated. Your access token is invalid (or) expired. Please regenerate the token from IoT Dashboard and use it'

    __speech_recognizer = None
    __TEXT_TO_SPEECH_SERVICE_NAME = 'AWS_POLLY'
    __SPEECH_TO_TEXT_SERVICE_NAME = 'GOOGLE_CLOUD_SPEECH'


    __is_speaking = False

    def __init__(self, access_token):
        Config.set_access_token(access_token)
        self.__set_access_token(access_token)
        self.__initialise_assistant()

    def __set_access_token(self, access_token):
        self.access_token = access_token
        self.__headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

    def __get_error_message(self, status_code):
        error_message = {
            'error': 'Failed to communicate with the server',
            'status_code': status_code
        }
        return error_message

    def __get_status_message(self, status, message):
        speech_status = {
            'status': status,
            'message': message
        }
        return speech_status

    def __initialise_assistant(self):

        self.__fetch_aws_credentials()
        
        self.__fetch_google_cloud_credentials()

        self.__polly_client = boto3.client(
            'polly',
            aws_access_key_id=self.__aws_credentials.access_key_id,
            aws_secret_access_key=self.__aws_credentials.secret_key,
            region_name=self.__aws_credentials.region_name
        )

        self.__voices = self.get_voices()

        self.__initialise_speech_recognizer()

        self.__initialised_assistant = True

    def __initialise_speech_recognizer(self):


        try:
            import pyaudio
            p = pyaudio.PyAudio()
            device_info = p.get_default_input_device_info()
            self.microphone = speech_recognition.Microphone()

            self.__speech_recognizer = speech_recognition.Recognizer()
            
            self.adjust_for_ambient_noise()

        except IOError:
            pass
        except ImportError:
            pass

    def adjust_for_ambient_noise(self):
        
        """Adjusts the speech recognizer's energy threshold automatically based on the current ambient noise.
        """

        if self.microphone == None:
            raise SpeechRecognitionError(604, 'Microphone unavailable')
        with self.microphone as source:
            self.__speech_recognizer.adjust_for_ambient_noise(
                source, duration=3)

        self.ambient_noise_threshold = self.__speech_recognizer.energy_threshold

    @property
    def ambient_noise_threshold(self):
        """Get or set the threshold which determines how sensitive the recognizer is to when recognition should start. Higher values mean that it will be less sensitive, which is useful if you are in a loud room.
        """
        return self.__speech_recognizer.energy_threshold

    @ambient_noise_threshold.setter
    def ambient_noise_threshold(self, value):

        self.__speech_recognizer.energy_threshold = value

    @property
    def microphone_device_index(self):
        """Get or set the index of the microphone device to be used.
        """
        return self.microphone.device_index

    @microphone_device_index.setter
    def microphone_device_index(self, value):
        self.microphone.device_index = value

    def get_voices(self):
        """Returns the list of voices that are available for use.

        Returns:
            list: A list of dictionaries containing different voices with their properties.

        Example:

            The following example shows how to delete a thing::

                voices = assistant.get_voices()
                print(voices)

            **Expected Output**::

                [
                    {
                        "Gender": "Female",
                        "Id": "Joanna",
                        "LanguageCode": "en-US",
                        "LanguageName": "US English",
                        "Name": "Joanna"
                    },
                    {
                        "Gender": "Female",
                        "Id": "Salli",
                        "LanguageCode": "en-US",
                        "LanguageName": "US English",
                        "Name": "Salli"
                    },
                   ...
                ]
        """

        polly_voices = []

        response = self.__polly_client.describe_voices(LanguageCode='en-US')
        for voice in response['Voices']:

            polly_voices.append(voice)

        response = self.__polly_client.describe_voices(LanguageCode='en-GB')

        for voice in response['Voices']:

            polly_voices.append(voice)

        response = self.__polly_client.describe_voices(LanguageCode='en-AU')

        for voice in response['Voices']:
            polly_voices.append(voice)

        response = self.__polly_client.describe_voices(LanguageCode='en-IN')

        for voice in response['Voices']:
            polly_voices.append(voice)
        # sorted_voice_list = sorted(
        #     response['Voices'], key=lambda k: k['LanguageCode'])
        return polly_voices

    def speak(self, text, voice_id='Joanna', background=False):
        """Speaks the given text.

        Parameters:
            text (str): Text to speak.
            voice_id (str, optional): The voice Id to be used. Default Id is ``Joanna``.
            background(bool, optional):  If ``True``, start a background thread to continue speaking and return immediately. If ``False`` (the default), only return when the speech is finished.
        Returns:
            dict: A dictionary containing the status of the text to speech conversion.

        Example:

            The following example shows how to delete a thing::

                status = assistant.speak('Hii! Hello. Welcome!')
                print(status)
                # status = assistant.speak('Hii! Hello. Welcome!', 'Amy')
                # print(status)
        
            **Expected Output**::

                {'status': 'SUCCESS', 'message': 'Speech synthesis complete'}


        """
        # voice_index = voice_index - 1

        # if ((voice_index < 0) or (voice_index > len(self.__voices) - 1)):
        #     return self.__get_status_message('ERROR', 'Invalid voice id. Please specify a voice id between 1 to ' + str(len(self.__voices)))

        # voice = self.__voices[voice_index]
        quota_status = self.__check_quota_status(Config.TEXT_TO_SPEECH_SERVICE_CODE)
        if not quota_status:
            raise QuotaLimitReachedError(700, 'Your Text to Speech service\'s quota limit has been reached. Please visit IoT Dashboard to check and extend your quota.')
        if (isinstance(text, float)):
            text = round(text, 1)

        text = str(text)

        if not any(voice['Id'] == voice_id for voice in self.__voices):
            raise ValidationError(422, 'Invalid Voice Id')

        if not self.__initialised_assistant:
            self.__initialise_assistant()

        response = self.__polly_client.synthesize_speech(
            OutputFormat='ogg_vorbis',
            Text=text,
            TextType='text',
            VoiceId=voice_id,
        )

        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output_mp3 = "speech.ogg"

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output_mp3, "wb") as file:
                        file.write(stream.read())
                    pygame.mixer.init()
                    pygame.mixer.music.load(output_mp3)
                    pygame.mixer.music.play()
                    self.__is_speaking = True

                    if background:
                        thread = threading.Thread(
                            target=self.__handle_text_to_speech_completion, args=([text]))
                        thread.daemon = True
                        thread.start()
                    else:
                        self.__handle_text_to_speech_completion(text)

                except IOError as error:
                    raise error

        else:
            return self.__get_status_message('ERROR', 'No audio stream received from server')
        

        return self.__get_status_message('SUCCESS', 'Speech successfully synthesised')
    
    
    def __handle_text_to_speech_completion(self, text):
        number_of_characters = len(text)
        session = FuturesSession()
        payload = {
            # 'service_name' : self.__TEXT_TO_SPEECH_SERVICE_NAME,
            'service_code': Config.TEXT_TO_SPEECH_SERVICE_CODE,
            'value' : number_of_characters
        }
        future = session.post(Config.SPRWIO_GATEWAY_URL +
                     'activity', headers=self.__headers, data=payload, background_callback=self.__on_activity_updated)
       
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        self.__is_speaking = False
        pygame.mixer.quit()

    def __check_quota_status(self, code):

        try:
            json_response = requests.get(
                Config.SPRWIO_GATEWAY_URL + 'services/' + str(code) + '/quota-status', headers=self.__headers)

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response.data.quota_status

        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        elif json_response.status_code == 401:
            raise AuthenticationError(
                json_response.status_code, self.__authentication_error_message)
        else:
            raise Error(Exception(response))


    @property
    def is_speaking(self):
        """Get the status whether assistant is currently speaking or not. ``True`` if the assistant is speaking and ``False`` otherwise.
        """
        return self.__is_speaking

    def recognize_speech(self, language='en-US', include_words=None, timeout=None):
        
        """Listens for speech input and converts it into text.
        

        Parameters:
            language (str, optional): The language of the speech as a BCP-47 language tag. Example: "en-US". See `Language Support <https://cloud.google.com/speech-to-text/docs/languages/>`_ for a list of the currently supported language codes.
            include_words (str, optional): A list of strings containing words and phrases "hints" so that the speech recognition is more likely to recognize them.
            timeout (int, optional): The maximum number of seconds that this will wait for a phrase to start before giving up and throwing an ``WaitTimeoutError`` exception. If ``timeout`` is ``None``, there will be no wait timeout.
        Returns:
            str: Text recognized from the given speech
        Raises:
            RequestError: If the cloud speech service is not reachable.
            UnknownValueError: If the audio is not understandable / or any miscellaneous error.
            WaitTimeoutError: If maximum number of seconds has elapsed while waiting for a phrase to start
            All the exceptions are based from ``SpeechRecognitionError``
        Example:

            The following example shows how to do speech recognition::

                    try:
        
                        text = assistant.recognize_speech(language='en-IN', include_words=['Robotics', 'IOT'], timeout=10)
                        print(text)
                         
                    except exceptions.SpeechRecognitionError as e:
                        print(e)

        """
        quota_status = self.__check_quota_status(
            Config.SPEECH_TO_TEXT_SERVICE_CODE)
        if not quota_status:
            raise QuotaLimitReachedError(
                700, 'Your Speech to Text service\'s quota limit has been reached. Please visit IoT Dashboard to check and extend your quota.')

        if self.microphone == None:
            raise SpeechRecognitionError(604, 'Microphone unavailable')

        try:
            with self.microphone as source:
                audio = self.__speech_recognizer.listen(
                    source, timeout=timeout)
            
            try:
                text = self.__speech_recognizer.recognize_google_cloud(
                    audio, credentials_json=self.__google_cloud_credentials, language=language, preferred_phrases=include_words)
                
                self.__handle_speech_to_text_completion(self.__speech_recognizer.audio_length)

                return text

            except speech_recognition.UnknownValueError as e:
                raise UnknownValueError(
                    601, 'Could not understand the audio')

            except speech_recognition.RequestError as e:
                raise RequestError(
                    602, 'Could not request results from the Cloud Speech service: ' + str(e))

        except speech_recognition.WaitTimeoutError as e:
            raise WaitTimeoutError(
                603, 'Listening timed out while waiting for phrase to start')

    def __handle_speech_to_text_completion(self, audio_length):
        
        session = FuturesSession()
        payload = {
            # 'service_name' : self.__SPEECH_TO_TEXT_SERVICE_NAME,
            'service_code': Config.SPEECH_TO_TEXT_SERVICE_CODE,

            'value': audio_length
        }
        future = session.post(Config.SPRWIO_GATEWAY_URL +
                     'activity', headers=self.__headers, data=payload, background_callback=self.__on_activity_updated)
    
    def print_microphone_list(self):

        """Prints the available list of microphones.
        """
        for index, name in enumerate(self.microphone.list_microphone_names()):
            print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(
                index, name))

    def get_datetime_from_text(self, text, source_time=datetime.datetime.now(), time_zone=None):

        """Parses the given text to extract and return datetime from it.

        Parameters:
            text (str): Text from which datetime must be extracted,
            source_time (datetime, optional): Reference time to be used as a base for computing actual datetime extracted from the text. Default value is current datetime.
            time_zone (str, optional):  Timezone to be applied for the generated datetime object. Eg: ``Asia/Kolkata``. See `Timezone datatbase <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones/>`_ for list of valid timezones.
        Returns:
            datetime: Object containing date and time.

        Example:
            The following example shows how to retreive the current date and time::
                
                print(assistant.get_current_datetime())
                source_time = assistant.get_current_datetime() + assistant.datetime_offset(days=2)
                print(source_time)
                time = assistant.get_datetime_from_text('Can you Set an alarm at 9 PM', source_time=source_time)
                print(time)

            **Expected Output**::
                 
                2017-12-29 18:05:00
                2017-12-31 18:05:00
                2017-12-31 21:00:00

        """

        calendar = parsedatetime.Calendar()
        reference_time = datetime.datetime.now()
        time_zone_info = None
        if (source_time != None):
            reference_time = source_time
        if (time_zone != None):
            time_zone_info = timezone(time_zone)

        return calendar.parseDT(text, reference_time, tzinfo=time_zone_info)[0]

    def get_current_datetime(self):
        """Return the current local date and time.

        Returns:
            datetime: Object containing current local date and time.

        Example:
            The following example shows how to retreive the current date and time::
                
                now = assistant.get_current_datetime()
                print(now)

            **Expected Output**::

                2017-12-31 16:23:46.391277

        """

        return datetime.datetime.now()

    def datetime_offset(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        """Returns a duration which can be used for manipulating dates and times.
        
        All parameters are optional and default to 0. Parameters may be ints, longs, or floats, and may be positive or negative.

        Parameters:
            days: Number of days.
            seconds: Number of seconds.
            microseconds: Number of microseconds.
            milliseconds: Number of milliseconds.
            minutes: Number of minutes.
            hours: Number of minutes.
            weeks: Number of weeks.

        Returns:
            datetime.timedelta: A timedelta object representing a duration.


        Example:
            The following example shows how to add certain duration to a datetime::
                
                now = assistant.get_current_datetime()
                print(now)
                updated_time = now + assistant.datetime_offset(hours=2)
                print(updated_time)

            **Expected Output**::

                2017-12-31 16:23:46.391277
                2017-12-31 18:23:46.391277

        """
        return datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds,
                                  milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    # def convert_to_datetime(self, time):

    #     return datetime.datetime.strptime(time, "%Y-%m-%d %I:%M %p")

    def get_time_in_words(self, hours=0, minutes=0):
        """Returns the time specified using hours and minutes in words format.
        
        Parameters:
            hours: Number of hours
            minutes: Number of minutes
        
        Returns:
            str: Time in words

        Example:
            The following example shows how to convert the given time to words::
                
                now = assistant.get_current_datetime()
                print(now)
                time_in_words = assistant.get_time_in_words(now.hour, now.minute)
                print(time_in_words)

            **Expected Output**::

                2017-12-31 16:23:46.391277
                Four Twenty three PM

        """
        if ((hours < 0) or (hours > 23)):
            return self.__get_status_message('ERROR', 'Hours should be between 0 to 23')
        if ((minutes < 0) or (minutes > 59)):
            return self.__get_status_message('ERROR', 'Minutes should be between 0 to 59')
        msg = ""

        hours_in_12 = hours % 12
        if (hours_in_12 == 0):
            hours_in_12 = 12

        if (minutes == 0):
            hour_in_words = self.__number_in_words[hours_in_12 - 1]
            msg = hour_in_words + " o'clock"  # in the morn,eve,afternoon,nite
            if (hours == 0):
                msg = msg + " in the midnight"
            elif (hours > 0 and hours < 12):
                msg = msg + " in the morning"
            elif (hours == 12):
                msg = msg + " in the noon"
            elif (hours > 12 and hours < 17):
                msg = msg + " in the afternoon"
            elif (hours >= 17 and hours < 20):
                msg = msg + " in the evening"
            elif (hours >= 20 and hours < 24):
                msg = msg + " in the night"

        else:
            time_meridian = ''
            if hours >= 0 and hours < 12:
                time_meridian = 'AM'
            else:
                time_meridian = 'PM'
            hour_in_words = self.__number_in_words[hours_in_12 - 1]
            minutes_in_words = self.__number_in_words[(minutes - 1)]

            minutes_in_words = self.__number_in_words[(minutes - 1)]
            msg = str(hour_in_words) + ' ' + \
                str(minutes_in_words) + ' ' + time_meridian

            # hour_in_words = self.words[hours_in_12 - 1]
            # minutes_in_words = self.words[(60 - minutes - 1)]
            # msg = header + minutes_in_words + " to " + hour_in_words + "."

        return msg

    # def get_time_in_words(self, time):
    #     hours = time.hour
    #     minutes = time.minute

    #     if ((hours < 0) or (hours > 23)):
    #         return self.__get_status_message('ERROR', 'Hours should be between 0 and 23')
    #     if ((minutes < 0) or (minutes > 59)):
    #         return self.__get_status_message('ERROR', 'Minutes should be between 0 and 59')

    #     msg = ""

    #     hours_in_12 = hours % 12
    #     if (hours_in_12 == 0):
    #         hours_in_12 = 12

    #     if (minutes == 0):
    #         hour_in_words = self.__number_in_words[hours_in_12 - 1]
    #         msg = hour_in_words + " o'clock"  # in the morn,eve,afternoon,nite
    #         if (hours == 0):
    #             msg = msg + " in the midnight"
    #         elif (hours > 0 and hours < 12):
    #             msg = msg + " in the morning"
    #         elif (hours == 12):
    #             msg = msg + " in the noon"
    #         elif (hours > 12 and hours < 17):
    #             msg = msg + " in the afternoon"
    #         elif (hours >= 17 and hours < 20):
    #             msg = msg + " in the evening"
    #         elif (hours >= 20 and hours < 24):
    #             msg = msg + " in the night"

    #     else:
    #         time_meridian = ''
    #         if hours >= 0 and hours < 12:
    #             time_meridian = 'AM'
    #         else:
    #             time_meridian = 'PM'
    #         hour_in_words = self.__number_in_words[hours_in_12 - 1]
    #         minutes_in_words = self.__number_in_words[(minutes - 1)]

    #         minutes_in_words = self.__number_in_words[(minutes - 1)]
    #         msg = str(hour_in_words) + ' ' + \
    #             str(minutes_in_words) + ' ' + time_meridian

    #         # hour_in_words = self.words[hours_in_12 - 1]
    #         # minutes_in_words = self.words[(60 - minutes - 1)]
    #         # msg = header + minutes_in_words + " to " + hour_in_words + "."

    #     return msg
    # def get_month_in_words(self, date):
    #     month_number = date.month
    #     month_text = self.__month_in_words[month_number-1]
    #     return month_text

    def get_month_in_words(self, month_number):
        """Returns the name of the month for the given month number.
        
        Parameters:
            month_number: Month Number
        
        Returns:
            str: Name of the month

        Example:
            The following example shows how to convert the given month number to name::
                
                now = assistant.get_current_datetime()
                print(now)
                
                month = assistant.get_month_in_words(now.month)
                print(month)

            **Expected Output**::

                2017-12-31 16:23:46.391277
                December

        """

        if ((month_number < 1) or (month_number > 12)):
            return self.__get_status_message('ERROR', 'Month should be between 1 and 12')

        month_text = self.__month_in_words[month_number - 1]
        return month_text

    def get_random_message(self, message_list):
        """Returns a random message chosen from the given list.
        
        Parameters:
            message_list (list): List of messages.
        
        Returns:
            str: A randomly selected message.
        
        Example:
            
            The following example shows how to retrieve a random message from a list of messages::
                
                messages = [
                    "Hello", "Hi", "Test", "Testing", "Good", "Bye"
                ]

                random_message = assistant.get_random_message(messages)
                print(random_message)

            **Expected Output**::

                Test

        """

        max_range = len(message_list) - 1
        random_index = randint(0, max_range)
        return message_list[random_index]
    
    def __on_activity_updated(self, sess, resp):
        resp.data = resp.json()
        # print('Response: ', resp.data)

    def __fetch_aws_credentials(self):
        try:
            json_response = requests.get(
                Config.SPRWIO_GATEWAY_URL + 'aws-credentials', headers=self.__headers)

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            self.__aws_credentials = response.data
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)
        elif json_response.status_code == 401:
            raise AuthenticationError(
                json_response.status_code, self.__authentication_error_message)
        else:
            raise Error(Exception(response))

    def __fetch_google_cloud_credentials(self):
        try:
            json_response = requests.get(
                Config.SPRWIO_GATEWAY_URL + 'google-cloud-credentials', headers=self.__headers)

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            self.__google_cloud_credentials = response.data.credentials
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)
        elif json_response.status_code == 401:
            raise AuthenticationError(
                json_response.status_code, self.__authentication_error_message)
        else:
            raise Error(Exception(response))
