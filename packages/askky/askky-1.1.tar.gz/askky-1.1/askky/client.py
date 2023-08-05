import json
import requests

class Client:
    def __init__(self,privateKey=None):
        self.base_url = "https://api.askky.co/"
        self.privateKey = privateKey

    def trigger_survey(self, survey_id, user_id, **kwargs):
        """"
        trigger specific survey for a user
        Args:
            survey_id : Id of the Survey that you want to call
            user_id : Id of the user to whom you want to show the Survey
        Returns:
            Success Response Dict
        """
        
        
        url = str(self.base_url) + str('trigger/form/')
        data = {}
        data["privateKey"] = self.privateKey
        data["campaignId"] = survey_id
        data["userId"] = user_id
        print ('data',json.dumps(data))
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url,data=str(json.dumps(data)),headers=headers)

        return response
