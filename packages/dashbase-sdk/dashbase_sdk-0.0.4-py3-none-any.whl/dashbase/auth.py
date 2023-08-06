import requests
import click
import logging
from dashbase import utils


class AuthClient(object):
    def __init__(self, host: str):
        self.headers = {'Accept': 'application/json'}
        self.host = host

    def get_token(self, user, password) -> bytes:
        path = "/basic"

        res = requests.post("{}{}".format(self.host, path), auth=(user, password))
        try:
            res.raise_for_status()
        except requests.HTTPError:
            return b""

        return res.content

    @staticmethod
    def get_dashbase_token_in_local(api_host, ignore_input: bool = False, auth_host=None) -> str:
        path = utils.get_setting_path().joinpath("dashbase.token")

        if not path.exists() and not ignore_input:
            y = click.confirm("Can't found token in local, do you want input your dashbase account to get token",
                              default=True)
            if not auth_host:
                _api_host = requests.utils.urlparse(api_host)
                default_auth_host = _api_host._replace(netloc="{}:{}".format(_api_host.hostname, "9678")).geturl()
                auth_host = click.prompt("please input your dashbase auth host", default=default_auth_host)

            click.echo("\nnow use auth_host: {}\n".format(click.style(auth_host, fg="green")))

            while y:
                user = click.prompt("your dashbase account")
                password = click.prompt("your dashbase password", hide_input=True)

                auth_client = AuthClient(auth_host)
                token = auth_client.get_token(user, password)
                if not token:
                    click.secho("get token failed, please check your account info\n", fg="yellow")
                    continue

                with path.open("wb") as f:
                    f.write(token)
                click.secho("get token success, saved token to:{}".format(path), fg="green")
                break

        if path.exists():
            logging.debug("use local token, path:{}".format(path))
            return path.open().readline()

        logging.debug("not use local token".format(path))
        return ""
