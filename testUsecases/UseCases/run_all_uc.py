import uc1_oem_enroll_1 as uc1
import uc2_oem_enroll_2 as uc2
import uc3_dev_model_reg as uc3
import uc4_dev_self_reg as uc4
import uc5_consumer_buys_dev as uc5
import uc6_dev_claim as uc6
import uc7_dev_twin as uc7
import uc8_dev_untwin as uc8

import time

def main():
    print("UC1: \n")
    dave_inv = uc1.main()
    time.sleep(2)
    print("UC2: \n")
    uc2.main(dave_inv[0]['connection_id'])
    time.sleep(2)
    print("UC3: \n")
    uc3.main()
    time.sleep(2)
    print("UC4: \n")
    uc4.main()
    time.sleep(2)
    print("UC5: \n")
    uc5.main()
    time.sleep(2)
    print("UC6: \n")
    uc6.main()
    time.sleep(2)
    print("UC7: \n")
    uc7.main()
    time.sleep(2)
    print("UC8: \n")
    uc8.main()


if __name__ == "__main__":
    main()