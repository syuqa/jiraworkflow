import json
from datetime import datetime, timedelta

import requests
from .models import TimettaConnect

class WPAuth:
    def __init__(self):
        self.auth_url = 'https://auth.timetta.com/connect/token'
        self.main_auth_data = {"client_id": "external", "scope": "all offline_access"}
        self.formatter_now = '%Y-%m-%d %H:%M:%S.%f'

    def get_auth_token(self):
        auth_data = self.get_auth_data_from_account()
        token = None
        if auth_data is not None and 'created' in auth_data:
            created = datetime.strptime(auth_data["created"], self.formatter_now)
            if (datetime.now() - created).total_seconds() < auth_data["expires_in"]:
                token = auth_data['access_token']
            elif (datetime.now() - created).total_seconds() < timedelta(days=15).total_seconds():
                token = self.get_auth_token_from_refresh(auth_data['refresh_token'])
        if token is None:
            token = self.get_auth_token_from_password()
        return token
        
    def get_auth_token_from_password(self):
        try:
            account = TimettaConnect.objects.get(id=1)
            data = {**self.main_auth_data, "grant_type": "password", "username": account.username,
                    "password": account.password}
            res = requests.post(self.auth_url, data=data)
            print(res.text)
            if res.status_code == 200:
                res_json = res.json()
                res_json['created'] = str(datetime.now())
                self.set_auth_data_in_account(res_json)
                return res_json['access_token']
            return None
        except TimettaConnect.DoesNotExist:
            return None

    def get_auth_token_from_refresh(self, refresh_token) -> str or None:
        data = {**self.main_auth_data, "grant_type": "refresh_token",
                "refresh_token": refresh_token}
        res = requests.post(self.auth_url, data=data)
        print(res.text)
        if res.status_code == 200:
            res_json = res.json()
            res_json['created'] = str(datetime.now())
            self.set_auth_data_in_account(res_json)
            return res_json['access_token']
        return None

    def get_auth_header(self):
        auth_token = self.get_auth_token()
        if auth_token is not None:
            return {"Authorization": f"Bearer {auth_token}"}
        return None

    def set_auth_data_in_account(self, data: dict):
        try:
            account = TimettaConnect.objects.get(id=1)
            account.tokens = data
            account.save()
        except TimettaConnect.DoesNotExist:
            pass

    def get_auth_data_from_account(self) -> dict or None:
        try:
            account = TimettaConnect.objects.get(id=1)
            return account.tokens
        except TimettaConnect.DoesNotExist:
            return None

        
        
    