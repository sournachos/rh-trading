import pyotp
# Make changes to this file to get your MFA set up - do NOT commit these changes

def log_in():
    # grab the key from Robinhood:
    # Security & Privacy > Two-Factor Authentication > Authenticator app
    # Save the key in your .env as MFA_CODE="your_key"
    # Copy/paste the key below and on your Robinhood app click 'Continue' on the page with the key
    totp = pyotp.TOTP("paste_key_here").now()
    # Once you run this function/page, 
    # copy the totp code printed and put it into your Robinhood app to link it
    print(totp)


log_in()
