import smtplib
import dns.resolver

# Simple Regex for syntax checking

mx_cache = {}

def get_mx_record(domain):
    # Check if the MX record is already cached
    if domain in mx_cache:
        return mx_cache[domain]

    # If not cached, perform a DNS lookup
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        # Cache the result
        mx_cache[domain] = mx_record
        print(domain+" "+mx_record)
        return mx_record
    
    except Exception as e:
        print(domain+" none")
        return None  # Handle the error as needed

def checkEmail(addressToVerify):
    code = 'na'
    addressToVerify = addressToVerify.strip().lower()
   
    try:
        splitAddress = addressToVerify.split('@')
        domain = str(splitAddress[1])
    except:
        return "not an email"
        exit
   
    try:
        # MX record lookup
        records = dns.resolver.resolve(domain, 'MX')
        # mxRecord = records[0].exchange
        mxRecord = get_mx_record(domain)
        # SMTP lib setup
        server = smtplib.SMTP()
        # uncomment the below line if you want to see full output.
        #server.set_debuglevel(1)

        #This is just a fake email that doesn't probably exist for smtp.mail(fromAddress)  
        fromAddress = 'just_a_place_holder@domain.com'

        # SMTP Conversation
        server.connect(mxRecord)
        server.helo(server.local_hostname) ### server.local_hostname(Get local server hostname)
        server.mail(fromAddress)
        code, message = server.rcpt(str(addressToVerify))
        server.quit()

        # Assume SMTP response 250 is success
        if code == 250:
            rtn = 'ok'
        else:
            if code == 550 :
                if 'User Unknown' in str(message):
                    rtn = 'no user'
                else:
                    rtn = 'unknow'
            else:
                rtn = 'no user'              
    except Exception as e:
        rtn = f"no domain: {e}"
    
    final_rtn = {
        'message' : rtn,
        'code'    : code
    }
        
    return final_rtn


