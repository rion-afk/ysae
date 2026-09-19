import config
from google_auth_oauthlib.flow import InstalledAppFlow

def main():
    print("Avvio procedura autorizzazione OAuth2...")
    flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS, config.SCOPES)
    creds = flow.run_local_server(port=0)
    with open(str(config.BASE / "token.json"), "w") as token:
        token.write(creds.to_json())
    print("\n✅ token.json generato con successo! Il bot ora ha accesso al canale.")

if __name__ == "__main__":
    main()
