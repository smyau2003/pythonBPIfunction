import aiodns
import aiosmtplib
import asyncio

# Simple Regex for syntax checking (not used in this code)

mx_cache = {}

async def get_mx_recordold(domain):
    # Check if the MX record is already cached
    if domain in mx_cache:
        return mx_cache[domain]
    
    # If not cached, perform a DNS lookup
    resolver = aiodns.DNSResolver()
    try:
        records = await resolver.query(domain, 'MX')
        mx_record = str(records[0].exchange)
        # Cache the result
        mx_cache[domain] = mx_record
        print(f"{domain} {mx_record} abcd")
        return mx_record

    except Exception as e:
        print(e)
        return None  # Handle the error as needed
    
async def get_mx_record22(domain):
    # Check if the MX record is already cached
    if domain in mx_cache:
        return mx_cache[domain]
    
    # If not cached, perform a DNS lookup
    resolver = aiodns.DNSResolver()
    try:
        records = await resolver.query(domain, 'MX')
        if records:  # Check if there are any records
            mx_record = str(records[0].exchange)  # Access the exchange attribute of the first MX record
            # Cache the result
            mx_cache[domain] = mx_record
            print(f"{domain} {mx_record}")
            return mx_record
        else:
            print(f"No MX records found for {domain}")
            return None
    except Exception as e:
        print(f"abc {e}")
        return None  # Handle the error as needed    


async def get_mx_record(domain):
    # Check if the MX record is already cached
    if domain in mx_cache:
        return mx_cache[domain]
    
    # If not cached, perform a DNS lookup
    resolver = aiodns.DNSResolver()
    try:
        records = await resolver.query(domain, 'MX')
     
        if records:  # Check if there are any records
            #print(record)
            #     # Ensure you're accessing the correct attributes
            mx_record = str(records[0].host)
               
            # # Cache the result
            mx_cache[domain] = mx_record
            print(f"{domain} MX records: {mx_record}")
            return mx_record
        else:
            print(f"No MX records found for {domain}")
            return None
    except Exception as e:
       
        print("ABC")
        return None  # Handle the error as needed
    

async def check_email(address_to_verify):
    address_to_verify = address_to_verify.strip().lower()
    
    try:
        split_address = address_to_verify.split('@')
        domain = str(split_address[1])
    except Exception:
        return {"message": "not an email", "code": None}

    try:
        # MX record lookup
        mx_record = await get_mx_record(domain)
        print(mx_record)
        if mx_record is None:
            return {"message": "no domain", "code": None}

        # SMTP lib setup
        from_address = 'just_a_place_holder@domain.com'

        # SMTP Conversation
        async with aiosmtplib.SMTP(hostname=mx_record) as server:
            await server.helo()
            await server.mail(from_address)
            code, message = await server.rcpt(address_to_verify)

        # Assume SMTP response 250 is success
        if code == 250:
            rtn = 'ok'
        else:
            if code == 550:
                if 'User Unknown' in str(message):
                    rtn = 'no user'
                else:
                    rtn = 'unknown'
            else:
                rtn = 'no user'
    except Exception as e:
        rtn = f"no domain22: {e}"
        code = None

    final_rtn = {
        'message': rtn,
        'code': code
    }
        
    return final_rtn




