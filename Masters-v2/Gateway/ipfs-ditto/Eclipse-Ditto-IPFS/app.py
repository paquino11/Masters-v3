import schedule
import time
import helper

print("Listening for Ditto Things started....")

helper.save_ditto_things_ipfs()

schedule.every(30).seconds.do(helper.save_ditto_things_ipfs)



while True:
    schedule.run_pending()
    print("sent to fabric")
    time.sleep(1)
