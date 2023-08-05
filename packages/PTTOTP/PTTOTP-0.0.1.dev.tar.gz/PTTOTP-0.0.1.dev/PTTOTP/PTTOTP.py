import sys
import traceback
import time
import json
import getpass
from time import gmtime, strftime
from PTTLibrary import PTT
import pyotp

def log(InputMessage):
    TotalMessage = "[" + strftime("%m-%d %H:%M:%S") + "] " + InputMessage
    try:
        print(TotalMessage.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding))
    except Exception:
        print(TotalMessage.encode('utf-8', "replace").decode('utf-8'))

def getTime():
    return strftime("%H:%M")

QRCodeHTMLSample = '''
<!DOCTYPE html>
<html>
  <body>
    <canvas id="qr"></canvas>

    <script src="./Res/qrious.js"></script>
    <script>
      (function() {
        var qr = new QRious({
          element: document.getElementById('qr'),
          value: '==Value=='
        });
      })();
    </script>
  </body>
</html>
'''

try:
    with open('Account.txt') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
except:
    ID = input('請輸入帳號: ')
    Password = getpass.getpass('請輸入密碼: ')
    with open('Account.txt', 'w') as AccountFile:
        AccountFile.write('{"ID":"' + ID + '", "Password":"' + Password + '"}')

try:
    with open('Secret.txt') as SecretFile:
        OTPSecret = SecretFile.read()
except:
    print('沒有偵測到密鑰檔案，如果要恢復金鑰請將「Secret.txt」放置在資料夾中')
    print('或者將會為您產生一個全新金鑰。')
    print('初次使用請直接繼續並產生全新金鑰')
    C = input('繼續？[Y/n] ').lower()
    if C == 'y' or C == '':
        OTPSecret = pyotp.random_base32()
        with open('Secret.txt', 'w') as SecretFile:
            SecretFile.write(OTPSecret)
    else:
        sys.exit()

OTPURL = pyotp.totp.TOTP(OTPSecret).provisioning_uri(ID, issuer_name="PTT OTP")
with open('QRCode.html', 'w') as QRCodeFile:
    QRCodeFile.write(QRCodeHTMLSample.replace('==Value==', OTPURL))

try:
    with open('LastPassword.txt') as LastPWFile:
        PasswordObj = json.load(LastPWFile)
        LastPassword = PasswordObj['LastPassword']
except:
    LastPassword = Password

OTP = pyotp.TOTP(OTPSecret)
PTTBot = PTT.Library()
ErrCode = PTTBot.login(ID, LastPassword)
if ErrCode != PTT.ErrorCode.Success:
    PTTBot.Log('登入失敗')
    sys.exit()

try:
    while True:
        CurrentOTP = OTP.now()

        if LastPassword != CurrentOTP:
            with open('LastPassword.txt', 'w') as LastPasswordFile:
                LastPasswordFile.write('{"PrePassword":"' + LastPassword + '", "LastPassword":"' + CurrentOTP + '"}')
            
            log('準備更改密碼 ' + LastPassword + ' -> ' + CurrentOTP)

            ErrCode = PTTBot.changePassword(LastPassword, CurrentOTP)
            # ErrCode = PTTBot.changePassword(Password, Password)
            if ErrCode != PTT.ErrorCode.Success:
                log('失敗')
                break

            LastPassword = CurrentOTP

        time.sleep(0.5)

except Exception as e:
        
    traceback.print_tb(e.__traceback__)
    print(e)
    PTTBot.Log('接到例外 啟動緊急應變措施')

PTTBot.logout()