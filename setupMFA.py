import pyotp


def log_in() -> dict | None:
    # grab the key from Robinhood (Security & Privacy section) and paste it below
    # save the value below in your .env as MFA_CODE
    totp = pyotp.TOTP("paste_key_here").now()
    # copy the code printed and put it into your Robinhood app to link it
    print(totp)


log_in()
