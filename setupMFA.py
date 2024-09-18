import pyotp
def log_in() -> dict | None:
    # grab the key from Robinhood and paste it below
    totp = pyotp.TOTP("paste_key_here").now()
    # save the value below in your .env as MFA_CODE
    print(totp)