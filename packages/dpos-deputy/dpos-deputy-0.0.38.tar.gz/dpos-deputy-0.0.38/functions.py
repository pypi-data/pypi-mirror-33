import dpostools.legacy as legacy
import arky.rest
from config import CONFIG


class Payouts:

    def __init__(self, network, delegate_address, pubkey, db_host, db_user, db_name,
                 db_pw, arky_network_name, printer, passphrase=None, second_passphrase=None,
                 rewardswallet=None):

        self.network = network
        self.delegate_address = delegate_address
        self.delegate_pubkey = pubkey
        self.delegate_passphrase = passphrase
        self.delegate_second_passphrase = second_passphrase
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_pw = db_pw
        self.rewardswallet = rewardswallet
        self.printer = printer
        self.arky_network_name = arky_network_name

    def calculate_raw_payouts(self, max_weight, blacklist):
        legacy.set_connection(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_pw
        )

        legacy.set_delegate(
            address=self.delegate_address,
            pubkey=self.delegate_pubkey,
        )
        self.printer.debug("Starting trueshare calculation")
        return legacy.Delegate.trueshare(max_weight=max_weight, blacklist=blacklist)

    def format_raw_payouts(self, payouts_dict, cover_fees, share):
        self.printer.debug("formatting raw payouts")
        for i in payouts_dict:
            if not cover_fees:
                payouts_dict[i]["share"] -= 0.1 * CONFIG[self.network]['coin_in_sat']
            payouts_dict[i]["share"] *= share
            self.printer.debug(payouts_dict[i])
        return payouts_dict

    def calculate_payouts(self, max_weight, cover_fees, share, blacklist=None):
        raw = self.calculate_raw_payouts(max_weight, blacklist)[0]
        return self.format_raw_payouts(raw, cover_fees=cover_fees, share=share)

    def transmit_payments(self, payouts, message, min_share):
        self.printer.debug("connecting to network: {}".format(self.network))
        arky.rest.use(self.arky_network_name)
        for ark_address in payouts:
            if payouts[ark_address]["share"] > min_share:
                res = arky.core.sendToken(payouts[ark_address]["share"], ark_address, self.delegate_passphrase,
                                    secondSecret=self.delegate_second_passphrase if self.delegate_second_passphrase else None,
                                    vendorField=message)
                if res["success"]:
                    self.printer.debug(res)
                else:
                    self.printer.warn(res)
            else:
                self.printer.debug("Insufficient built up balance for {}".format(payouts[ark_address]))

    def pay_voters(self, cover_fees, max_weight, share, min_share, message=None):
        self.printer.debug("calculating voter payouts")
        payouts = self.calculate_payouts(
            cover_fees=cover_fees,
            max_weight=max_weight,
            share=share)
        self.printer.debug("starting payment transmission")
        self.transmit_payments(
            payouts,
            message=message,
            min_share=min_share
        )
        self.printer.debug("transmission successful")

    def calculate_delegate_share(self, covered_fees, shared_percentage):
        legacy.set_connection(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_pw
        )

        last_reward_payout = legacy.DbCursor().execute_and_fetchone("""
                        SELECT blocks."timestamp"
                        FROM transactions
                        INNER JOIN blocks ON transactions."blockId" = blocks."id"
                        WHERE transactions."recipientId" = '{rewardwallet}'
                        AND transactions."senderId" = '{delegateaddress}'
                        ORDER BY blocks."timestamp" DESC 
                        LIMIT 1
                    """.format(
            rewardwallet=self.rewardswallet,
            delegateaddress=self.delegate_address
        ))

        if last_reward_payout is None:
            last_reward_payout = 0
        else:
            last_reward_payout = last_reward_payout[0]

        payouts = legacy.DbCursor().execute_and_fetchall("""
            SELECT SUM(transactions."amount"), SUM(transactions."fee")
            FROM transactions 
            INNER JOIN blocks on transactions."blockId" = blocks."id"
            WHERE transactions."senderId" = '{del_address}' 
            AND transactions."recipientId" != '{rewardswallet}'
            AND blocks."timestamp" > {ts_last_payout};
        """.format(del_address=self.delegate_address, ts_last_payout=last_reward_payout, rewardswallet=self.rewardswallet)
        )

        blocks = legacy.Delegate.blocks(self.delegate_pubkey)

        if covered_fees:

            delegate_share = float(payouts[0][0]) * (1 - shared_percentage) - float(payouts[0][1])
        else:
            delegate_share = float(payouts[0]) * (1-shared_percentage)

        for b in blocks:
            if b.timestamp > last_reward_payout:
                        delegate_share += b.totalFee

        return delegate_share

    # def calculate_delegate_share(self, covered_fees, shared_percentage):
    #     legacy.set_connection(
    #         host=self.db_host,
    #         database=self.db_name,
    #         user=self.db_user,
    #         password=self.db_pw)
    #
    #     payouts = legacy.Address.transactions(self.delegate_address)
    #     blocks = legacy.Delegate.blocks(self.delegate_pubkey)
    #
    #     last_reward_payout = legacy.DbCursor().execute_and_fetchone("""
    #             SELECT transactions."timestamp"
    #             FROM transactions
    #             WHERE transactions."recipientId" = '{rewardwallet}'
    #             AND transactions."senderId" = '{delegateaddress}'
    #             ORDER BY transactions."timestamp" DESC
    #             LIMIT 1
    #         """.format(
    #         rewardwallet=self.rewardswallet,
    #         delegateaddress=self.delegate_address
    #     ))[0]
    #
    #     delegate_share = 0
    #
    #     if covered_fees:
    #         txfee = 0.1 * CONFIG[self.network]['coin_in_sat']
    #     else:
    #         txfee = 0
    #
    #     for i in payouts:
    #         if i.recipientId == self.rewardswallet:
    #             del i
    #         else:
    #             if i.timestamp > last_reward_payout:
    #                 total_send_amount = (i.amount + txfee) / shared_percentage
    #                 delegate_share += total_send_amount - (
    #                             total_send_amount * shared_percentage + txfee)
    #
    #     for b in blocks:
    #         if b.timestamp > last_reward_payout:
    #             delegate_share += b.totalFee
    #
    #     return delegate_share
    #

    def pay_rewardswallet(self, covered_fees, shared_percentage, message=None):
        arky.rest.use(self.arky_network_name)
        share = self.calculate_delegate_share(
            covered_fees=covered_fees,
            shared_percentage=shared_percentage)
        self.printer.debug("calculated share is {}".format(share))

        self.printer.debug(text=("share:", share, "recipientId:", self.rewardswallet, "secret:", self.delegate_passphrase,
                           "secondSecret:", self.delegate_second_passphrase, "Vendorfield:", message))

        res = arky.core.sendToken(
            amount=share,
            recipientId=self.rewardswallet,
            secret=self.delegate_passphrase,
            # defaults to None if not initialized.
            secondSecret=self.delegate_second_passphrase if self.delegate_second_passphrase else None,
            vendorField=message if message else "Delegate's reward share.")
        self.printer.debug(res)

    def tip(self):
        arky.rest.use(self.arky_network_name)
        arky.core.sendToken(
            CONFIG[self.network]['tip'],
            CONFIG[self.network]['tipping_address'],
            self.delegate_passphrase,
            # defaults to None if not initialized.
            secondSecret=self.delegate_second_passphrase,
            )


