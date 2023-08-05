from pathlib import Path
import click
import pickle
import exceptions as e
from config import CONFIG
from functions import Payouts
from pprint import pprint
from encryption import Crypt
import constants as c
from raven.handlers.logging import SentryHandler
import logging
import db as i
from pid import PidFile
import subprocess
import help_texts as h
import validators as v
import os


def bash_command(cmd):
    subprocess.Popen(['/bin/bash', '-c', cmd])


def load_config(ctx, network):
    """
    Some boilerplate code for obtaining configuration dict from ctx.
    :return: config dict
    """
    config = ctx.obj['config']
    setting = config[network]
    if network not in CONFIG:
        if click.confirm("Unfamiliar with that network. Do you wish to set it now?", abort=True):
            set_config(ctx)

    printer = ctx.obj['printer']
    return setting, printer


class Verbose:
    def __init__(self, level, dsn=None):
        self.level = int(level)
        self.logger = logging.getLogger(__name__)
        if dsn:
            self.handler = SentryHandler(dsn)
            self.handler.setLevel(level)

    def debug(self, text, color=None):
        if self.level <= 10:
            self.logger.debug(text)
            click.echo(message=text, color=color)

    def info(self, text, color=None):
        if self.level <= 20:
            self.logger.info(text)
            click.echo(message=text, color=color)

    def log(self, text, color=None):
        self.logger.log(30, text)
        if self.level <= 30:
            click.echo(message=text, color=color)

    def warn(self, text, color=None):
        self.logger.error(text)
        if self.level <= 40:
            click.echo(message=text, color=color)

@click.group()
@click.option(
    '--config-file', '-c',
    type=click.Path(),
    default='/tmp/.dpos-CLI.cfg',
    help=h.CONFIG_FILE)
@click.option(
    '--verbose', '-v',
    type=click.Choice(["0", "10", "20", "30", "40", "50"]),
    default="20",
    help=h.VERBOSE)
@click.pass_context
def main(ctx, config_file, verbose):
    """
    Command line tool for delegates

    Currently supports:

        Ark
        devnet-Ark
        Kapu
        Test-Persona
        Persona

    """
    printer = Verbose(level=int(verbose))

    filename = os.path.expanduser(config_file)
    config = CONFIG

    if os.path.exists(filename):
        with open(filename, 'rb') as config_file:
            config = pickle.load(config_file)

    ctx.obj = {
        'config': config,
        'printer': printer,
    }

@main.command()
@click.pass_context
def enable_autocomplete(ctx):
    printer = ctx.obj['printer']
    home = str(Path.home())
    Path('{}/.bashrc'.format(home)).touch()

    # check if we already appended the script command.
    with open("{}/.bashrc".format(home), "r") as bashrc:
        lines = bashrc.readlines()
        for line in lines:
            if "{home}/deputy-complete.sh".format(home=home) in line:
                printer.warn("Already edited .bashrc!")
                printer.info("Running some commands.")
                subprocess.run("_DEPUTY_COMPLETE=source deputy > {home}/deputy-complete.sh".format(home=home),
                               shell=True)
                subprocess.run("chmod u+x {home}/deputy-complete.sh".format(home=home), shell=True)
                bash_command("{home}/deputy-complete.sh".format(home=home))
                printer.info("Done!")
                return

    with open("{}/.bashrc".format(home), "a") as bashrc:
        printer.info("Editing .bashrc")
        bashrc.write(". {home}/deputy-complete.sh".format(home=home))
        printer.info("Success!")

    printer.info("Running some commands.")
    subprocess.run("_DEPUTY_COMPLETE=source deputy > {home}/deputy-complete.sh".format(home=home), shell=True)
    subprocess.run("chmod u+x {home}/deputy-complete.sh".format(home=home), shell=True)
    bash_command("{home}/deputy-complete.sh".format(home=home))
    printer.info("Done!")


@main.command()
@click.password_option(
    '--password', '-p',
    type=click.STRING,
    hide_input=True,
    confirmation_prompt=True,
    help=h.PASSWORD)
@click.option(
    '--network', '-n',
    type=click.Choice([x for x in CONFIG.keys() if x != "virgin"]),
    default=None,
    help=h.NETWORK)
@click.option(
    '--setting', '-s',
    type=click.STRING,
    nargs=2,
    help=h.SETTING)
@click.pass_context
def set_config(ctx, network, setting, password):
    """
    Store configuration values in a file, e.g. the API key for OpenWeatherMap.
    """
    config = ctx.obj['config']
    printer = ctx.obj['printer']

    if not config["virgin"]:
        if not click.confirm("Override or add to previously set settings?", abort=True):
            return

    if not network:
        network = click.prompt("Please enter the network you wish to set")
        if network not in CONFIG:
            network = click.prompt("Invalid network, select from {}".format(list(CONFIG.keys())[1:]))
            if network not in CONFIG:
                raise e.InvalidNetwork("invalid network entered, exiting.")

        config["virgin"] = False

        config[network]["db_name"] = click.prompt("Please enter the name of the postgres database hosting the network")
        config[network]["db_host"] = click.prompt("Please enter the host of the database (probably localhost)")
        config[network]["db_user"] = click.prompt("Please enter the name of the postgres user")
        config[network]["db_password"] = click.prompt("Please enter the password of the postgres user", hide_input=True, confirmation_prompt=True)

        config[network]["delegate_address"] = click.prompt("Please enter your delegate address")
        config[network]["delegate_pubkey"] = click.prompt("Please enter your delegate pubkey")

        # passphrases are a list: passphrase, encryption status (True means encrypted)
        if click.confirm("Do want to store your passphrase?"):
            config[network]["delegate_passphrase"] = [click.prompt("Please enter your delegate passphrase"), False]
        else:
            config[network]["delegate_passphrase"] = None, None

        if click.confirm("Do want to store your second passphrase?"):
            config[network]["delegate_second_passphrase"] = [click.prompt("Please enter your delegate second passphrase"), False]
        else:
            config[network]["delegate_second_passphrase"] = None, None

        config[network]["share"] = click.prompt("Please enter your share percentage as a ratio (100% = 1, 50% = 0.5)", type=float)
        v.share_validator(None, None, config[network]["share"])

        config[network]["max_weight"] = config[network]["coin_in_sat"] * click.prompt("Please enter the max balance that a voter may have in {coin} (not {coin}toshi), "
                                                           "use 'inf' if you do not want to set a maximum (remaining staking reward gets distributed over other voters".format(coin=network), type=float)
        config[network]["cover_fees"] = click.confirm("Do you wish to cover transaction fees for your voters?")
        config[network]["min_share"] = click.prompt("What is the minimum built up balance a voter needs before receiving a payout?", type=float)
        config[network]["rewardswallet"] = click.prompt("To which address should the rewards be sent?", type=str)
        config[network]["message"] = click.prompt("Enter a message to send to your voters on payouts (if you don't want to send a message, leave it empty)")

        if click.confirm("Do you wish to blacklist voters?"):
            want_blacklist = True
            blacklist = config[network]["blacklist"]
            while want_blacklist:
                blacklist.append(click.prompt("enter an address to add to the blacklist"))
                if click.confirm("Do you wish to blacklist more voters?"):
                    want_blacklist = True
                else:
                    want_blacklist = False
            config[network]["blacklist"] = blacklist
        if click.confirm("Do you wish to enable raven logging?"):
            config[network]["raven_dsn"] = click.prompt("Enter your raven DSN")
        else:
            config[network]["raven_dsn"] = None

        if click.confirm("Do you want to setup a database for logging purposes?"):
            config[network]["db_name_{}_admin.".format(network)] = click.prompt("Please enter the name of the (non-existant) postgres database hosting the administration")
            config[network]["db_host_{}_admin".format(network)] = click.prompt("Please enter the host of the database (probably localhost)")
            config[network]["db_user_{}_admin".format(network)] = click.prompt("Please enter the name of the postgres user")
            config[network]["db_password_{}_admin".format(network)] = click.prompt("Please enter the password of the postgres user", hide_input=True)

    # Incase we are setting a value specifically through the CLI as a shortcut
    else:
        printer.info("Setting {nw}:{key} to {val}".format(nw=network, key=setting[0], val=setting[1]))
        config[network][setting[0]] = setting[1]

    # Encrypting the passphrases.
    Crypt().encrypt_config(config, network, password, printer)
    printer.info("Saving your settings...")
    pickle.dump(config, open("/tmp/.dpos-CLI.cfg", "wb"))
    printer.info("Saved!")
    return config


@main.command()
@click.password_option(
    '--password', '-p',
    type=click.STRING,
    hide_input=True,
    confirmation_prompt=True,
    help=h.PASSWORD)
@click.option(
    '--show_secret', '-sh',
    type=click.BOOL,
    default=False,
    help=h.SHOW_SECRET)
@click.pass_context
def inspect_config(ctx, show_secret, password):
    """
    Check my previously set configurations.
    """
    config = ctx.obj['config']
    printer = ctx.obj["printer"]
    Crypt().decrypt_config(config, password, printer)

    for network in config:
        if type(config[network]) == dict:
            printer.info(network.upper())
            for i in config[network]:
                if "passphrase" in i and not show_secret:
                    print("----", i, "---", "CENSORED PASSPHRASE")
                else:
                    print("----", i, "---", config[network][i])
        else:
            print(network.upper(), ":", config[network])


@main.command()
@click.option(
    '--cover_fees', '-cf',
    type=click.BOOL,
    default=False,
    help=h.COVER_FEES)
@click.option(
    '--max_weight', '-mw',
    type=click.FLOAT,
    default=float("inf"),
    help=h.MAX_WEIGHT,)
@click.option(
    '--share', '-s',
    type=click.FLOAT,
    callback=v.share_validator,
    default=None,
    help=h.SHARE)
@click.option(
    '--network', '-n',
    type=click.Choice([x for x in CONFIG.keys() if x != "virgin"]),
    prompt=True,
    help=h.NETWORK)
@click.option(
    '--store', '-st',
    type=click.BOOL,
    default=False,
    help=h.STORE)
@click.option(
    '--print', '-p',
    type=click.BOOL,
    default=True,
    help=h.PRINT)
@click.pass_context
def calculate_payouts(ctx, network, cover_fees, max_weight, share, store, print):
    """
    Calculate the pending payouts at this moment.
    """
    setting, printer = load_config(ctx, network)

    if cover_fees is None:
        cover_fees = setting["cover_fees"]
    if max_weight is None:
        max_weight = setting["max_weight"]
    if share is None:
        share = setting["share"]

    if store:
        try:
            db = i.DB(
                dbname=setting["db_name_{}_admin.".format(network)],
                host=setting["db_host_{}_admin".format(network)],
                user_name=setting["db_user_{}_admin".format(network)],
                password=setting["db_password_{}_admin".format(network)],
            )
        except KeyError:
            if click.confirm("Administration DB not set. Want to set it now?"):
                password = click.prompt("please enter your password", hide_input=True)

                config = ctx.obj['config']
                config[network]["db_name_{}_admin.".format(network)] = click.prompt(
                    "Please enter the name of the (non-existant) postgres database hosting the administration")
                config[network]["db_host_{}_admin".format(network)] = click.prompt(
                    "Please enter the host of the database (probably localhost)")
                config[network]["db_user_{}_admin".format(network)] = click.prompt(
                    "Please enter the name of the postgres user")
                config[network]["db_password_{}_admin".format(network)] = click.prompt(
                    "Please enter the password of the postgres user", hide_input=True)
                try:
                    # Encrypting the passphrases.
                    if not config[network]["delegate_passphrase"][1] and config[network]["delegate_passphrase"][0]:
                        printer.info("encrypting primary passhrase")
                        config[network]["delegate_passphrase"][0] = Crypt().encrypt(
                            string=config[network]["delegate_passphrase"][0], password=password)
                        config[network]["delegate_passphrase"][1] = True
                        printer.info("encrypted!")
                    if not config[network]["delegate_second_passphrase"][1] and \
                            config[network]["delegate_second_passphrase"][
                                0]:
                        printer.info("encrypting secondary passphrase")
                        config[network]["delegate_second_passphrase"][0] = Crypt().encrypt(
                            string=config[network]["delegate_second_passphrase"][0], password=password)
                        config[network]["delegate_second_passphrase"][1] = True
                        printer.info("encrypted!")
                except KeyError:
                    pass
            else:
                store = False

    calculator = Payouts(
        db_name=setting["db_name"],
        db_host=setting["db_host"],
        db_pw=setting["db_password"],
        db_user=setting["db_user"],
        network=network,
        delegate_address=setting["delegate_address"],
        pubkey=setting["delegate_pubkey"],
        arky_network_name=setting["arky"],
        printer=printer,
    )
    max_weight *= setting["coin_in_sat"]

    printer.info("Starting calculation...")
    payouts = calculator.calculate_payouts(
        cover_fees=cover_fees,
        max_weight=max_weight,
        share=share
    )

    if store:
        for y in payouts:
            db.store_payout(
                address=y,
                share=payouts[y]["share"],
                network=network,
                timestamp=payouts[y]["last_payout"]
            )

    for x in payouts:
        payouts[x]["share"] /= c.ARK
        payouts[x]["balance"] /= c.ARK

        try:
            if x in setting["blacklist"]:
                del payouts[x]
        except KeyError:
            pass

    if print:
        pprint(payouts)
        printer.info("Using the following configuration: \ncover_fees: {cf}\n max weight: {mw}\n share: {s}%\n".
               format(
                    cf=cover_fees,
                    mw="No max" if max_weight == float("inf") else max_weight,
                    s=share*100)
               )

@main.command()
@click.password_option(
    '--password', '-p',
    type=click.STRING,
    hide_input=True,
    confirmation_prompt=True,
    help=h.PASSWORD)
@click.option(
    '--message', '-m',
    type=click.STRING,
    default=None,
    help=h.MESSAGE)
@click.option(
    '--min_share', '-ms',
    type=click.FLOAT,
    default=None,
    help=h.MIN_SHARE)
@click.option(
    '--cover_fees', '-cf',
    type=click.BOOL,
    default=None,
    help=h.COVER_FEES)
@click.option(
    '--max_weight', '-mw',
    type=click.FLOAT,
    default=None,
    help=h.MAX_WEIGHT)
@click.option(
    '--share', '-s',
    type=click.FLOAT,
    callback=v.share_validator,
    default=None,
    help=h.SHARE)
@click.option(
    '--network', '-n',
    type=click.Choice([x for x in CONFIG.keys() if x != "virgin"]),
    prompt=True,
    help=h.NETWORK)
@click.pass_context
def payout_voters(ctx, network, cover_fees, max_weight, share, min_share, message, password):
    """
    Calculate and transmit payments to the voters.
    """
    config = ctx.obj['config']
    printer = ctx.obj["printer"]
    Crypt().decrypt_config(config, password, printer)
    setting = config[network]

    if cover_fees is None:
        cover_fees = setting["cover_fees"]
    if min_share is None:
        min_share = setting["min_share"]
    if max_weight is None:
        max_weight = setting["max_weight"]
    if message is None:
        message = setting["message"]
    if share is None:
        share = setting["share"]

    printer.log(
        """
        Using the following settings for the payout:
        
        Cover fees:                 {cover_fees}
        Min share (in full coins):  {min_share}
        Max weight:                 {max_weight}
        Message:                    {message}
        share:                      {share}
        """.format(
            cover_fees=cover_fees,
            min_share=min_share,
            max_weight=max_weight,
            message=message,
            share=share
        )
    )

    with PidFile(piddir='/tmp/'):
        printer.log("starting payment run")
        payer = Payouts(db_name=setting["db_name"], db_host=setting["db_host"], db_pw=setting["db_password"],
                        db_user=setting["db_user"], network=network, delegate_address=setting["delegate_address"],
                        pubkey=setting["delegate_pubkey"], rewardswallet=setting["rewardswallet"], passphrase=setting["delegate_passphrase"][0],
                        second_passphrase=setting["delegate_second_passphrase"][0] if setting["delegate_second_passphrase"][0] else None,
                        printer=printer, arky_network_name=setting["arky"])
        max_weight *= setting["coin_in_sat"]
        min_share *= setting["coin_in_sat"]

        printer.info("Calculating payments")
        payouts = payer.calculate_payouts(
                cover_fees=cover_fees,
                max_weight=max_weight,
                share=share)

        printer.info("transmitting payments")
        payer.transmit_payments(
                payouts,
                message=message,
                min_share=min_share,
        )
        printer.log("Payment run done!")


@main.command()
@click.option(
    '--covered_fees', '-cf',
    type=click.BOOL,
    default=None,
    help=h.COVERED_FEES,)
@click.option(
    '--shared_percentage', '-s',
    type=click.FLOAT,
    callback=v.share_validator,
    default=None,
    help=h.SHARED_PERCENTAGE)
@click.option(
    '--rewards_wallet', '-rw',
    type=click.STRING,
    default=None,
    help=h.REWARDS_WALLET,)
@click.option(
    '--network', '-n',
    type=click.Choice([x for x in CONFIG.keys() if x != "virgin"]),
    prompt=True,
    help=h.NETWORK)
@click.pass_context
def check_delegate_reward(ctx, network, covered_fees, shared_percentage, rewards_wallet):
    """
    Calculate the pending delegate reward.
    """
    config = ctx.obj["config"]
    printer = ctx.obj["printer"]
    setting = config[network]

    if covered_fees is None:
        covered_fees = setting["cover_fees"]
    if shared_percentage is None:
        shared_percentage = setting["share"]
    if rewards_wallet is None:
        rewards_wallet = setting["rewardswall" \
                                 "et"]

    calculator = Payouts(db_name=setting["db_name"], db_host=setting["db_host"], db_pw=setting["db_password"],
                         db_user=setting["db_user"], network=network, delegate_address=setting["delegate_address"],
                         pubkey=setting["delegate_pubkey"], arky_network_name=setting["arky"],
                         printer=printer, rewardswallet=rewards_wallet)

    delegate_share = calculator.calculate_delegate_share(
        covered_fees=covered_fees,
        shared_percentage=shared_percentage
    )
    printer.info("The built up share for the delegate is: {}".format(delegate_share/setting['coin_in_sat']))


@main.command()
@click.password_option(
    '--password', '-p',
    type=click.STRING,
    hide_input=True,
    confirmation_prompt=True,
    help=h.PASSWORD)
@click.option(
    '--network', '-n',
    type=click.Choice([x for x in CONFIG.keys() if x != "virgin"]),
    prompt=True,
    help=h.NETWORK)
@click.option(
    '--covered_fees', '-cf',
    type=click.BOOL,
    default=None,
    help=h.COVERED_FEES)
@click.option(
    '--shared_percentage', '-s',
    type=click.FLOAT,
    callback=v.share_validator,
    default=None,
    help=h.SHARED_PERCENTAGE)
@click.option(
    '--rewards_wallet', '-rw',
    type=click.STRING,
    default=None,
    help=h.REWARDS_WALLET)
@click.option(
    '--tip', '-t',
    type=click.BOOL,
    default=True,
    help=h.TIP)
@click.pass_context
def pay_rewardswallet(ctx, network, covered_fees, shared_percentage, tip, rewards_wallet, password):
    """
    Calculate and pay the current pending delegate reward share and transmit to the rewardwallet
    """
    config = ctx.obj["config"]
    printer = ctx.obj["printer"]
    Crypt().decrypt_config(config, password, printer)
    setting = config["network"]

    if covered_fees is None:
        covered_fees = setting["cover_fees"]
    if shared_percentage is None:
        shared_percentage = setting["share"]
    if rewards_wallet is None:
        rewards_wallet = setting["rewardswallet"]

    with PidFile(piddir='/tmp/'):

        printer.log("Calculating delegate reward")

        payer = Payouts(db_name=setting["db_name"], db_host=setting["db_host"], db_pw=setting["db_password"],
                        db_user=setting["db_user"], network=network, delegate_address=setting["delegate_address"],
                        pubkey=setting["delegate_pubkey"], arky_network_name=setting["arky"],
                        printer=printer, rewardswallet=rewards_wallet, passphrase=setting["delegate_passphrase"][0],
                        second_passphrase=setting["delegate_second_passphrase"][0])

        printer.log("Sending payment to delegate rewardswallet")
        payer.pay_rewardswallet(covered_fees=covered_fees, shared_percentage=shared_percentage)
        printer.log("Payment successfull.")

        if tip and not setting["testnet"]:
            payer.tip()


@main.command()
@click.option(
    '--network', '-n',
    type=click.Choice([x for x in CONFIG.keys() if x != "virgin"]),
    prompt=True,
    help=h.NETWORK)
@click.pass_context
def setup_postgres_db(ctx, network):
    """
    Setup a database for administrative purposes.
    """
    setting, printer = load_config(ctx, network)
    try:
        db = i.DB(
            dbname=setting["db_name_{}_admin.".format(network)],
            host=setting["db_host_{}_admin".format(network)],
            user_name=setting["db_user_{}_admin".format(network)],
            password=setting["db_password_{}_admin".format(network)],
        )
    except KeyError:
        if click.confirm("Administration DB not set. Want to set it now?"):
            password = click.prompt("please enter your password", hide_input=True)

            config = ctx.obj['config']
            config[network]["db_name_{}_admin.".format(network)] = click.prompt(
                "Please enter the name of the (non-existant) postgres database hosting the administration")
            config[network]["db_host_{}_admin".format(network)] = click.prompt(
                "Please enter the host of the database (probably localhost)")
            config[network]["db_user_{}_admin".format(network)] = click.prompt(
                "Please enter the name of the postgres user")
            config[network]["db_password_{}_admin".format(network)] = click.prompt(
                "Please enter the password of the postgres user", hide_input=True)
            try:
                # Encrypting the passphrases.
                if not config[network]["delegate_passphrase"][1] and config[network]["delegate_passphrase"][0]:
                    printer.info("encrypting primary passhrase")
                    config[network]["delegate_passphrase"][0] = Crypt().encrypt(
                        string=config[network]["delegate_passphrase"][0], password=password)
                    config[network]["delegate_passphrase"][1] = True
                    printer.info("encrypted!")
                if not config[network]["delegate_second_passphrase"][1] and config[network]["delegate_second_passphrase"][
                    0]:
                    printer.info("encrypting secondary passphrase")
                    config[network]["delegate_second_passphrase"][0] = Crypt().encrypt(
                        string=config[network]["delegate_second_passphrase"][0], password=password)
                    config[network]["delegate_second_passphrase"][1] = True
                    printer.info("encrypted!")
            except KeyError:
                pass

            printer.info("Saving your settings...")
            pickle.dump(config, open("/tmp/.dpos-CLI.cfg", "wb"))
            printer.info("Saved!")

            db = i.DB(
                dbname=setting["db_name_{}_admin.".format(network)],
                host=setting["db_host_{}_admin".format(network)],
                user_name=setting["db_user_{}_admin".format(network)],
                password=setting["db_password_{}_admin".format(network)],
            )
    printer.info("creating database {}".format(setting["db_name_{}_admin.".format(network)]))
    db.create_db()
    printer.info("setting up tables")
    db.create_table_users_payouts()


if __name__ == "__main__":
    main()