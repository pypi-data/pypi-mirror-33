"""
To make sure we do not save passphrases unencrypted, use this function
"""

from simplecrypt import encrypt, decrypt

class Crypt:

    def encrypt(self, string, password):
        return encrypt(password=password, data=string)

    def decrypt(self, crypt, password):
        return decrypt(password=password, data=crypt).decode("utf-8")

    def encrypt_config(self, config, network, password, printer):
        if not config[network]["delegate_passphrase"][1] and config[network]["delegate_passphrase"][0]:
            printer.info("encrypting primary passhrase")
            config[network]["delegate_passphrase"][0] = Crypt().encrypt(
                string=config[network]["delegate_passphrase"][0], password=password)
            config[network]["delegate_passphrase"][1] = True
            printer.info("encrypted!")
        if not config[network]["delegate_second_passphrase"][1] and config[network]["delegate_second_passphrase"][0]:
            printer.info("encrypting secondary passphrase")
            config[network]["delegate_second_passphrase"][0] = Crypt().encrypt(
                string=config[network]["delegate_second_passphrase"][0], password=password)
            config[network]["delegate_second_passphrase"][1] = True
            printer.info("encrypted!")

    def decrypt_config(self, config, password, printer):
        for network in config:
            if network == "virgin":
                continue

            try:
                if config[network]["delegate_passphrase"][1]:
                    printer.info("Decrypting primary passhrase")
                    config[network]["delegate_passphrase"][0] = Crypt().decrypt(crypt=config[network]["delegate_passphrase"][0],
                                                                             password=password)
                    config[network]["delegate_passphrase"][1] = False
                    printer.info("Decrypted!")
                if config[network]["delegate_second_passphrase"][1]:
                    printer.info("Decrypting secondary passphrase")
                    config[network]["delegate_second_passphrase"][0] = Crypt().decrypt(
                        crypt=config[network]["delegate_second_passphrase"][0], password=password)
                    config[network]["delegate_second_passphrase"][1] = False
                    printer.info("decrypted!")
            except KeyError:
                pass
