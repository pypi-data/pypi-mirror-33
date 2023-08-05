#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Dusan Klinec, ph4r05, 2018

from monero_serialize import xmrtypes, xmrserialize
from monero_glue.xmr.monero import TsxData, classify_subaddresses
from monero_glue.hwtoken import misc
from monero_glue.xmr import monero, mlsag2, ring_ct, crypto, common
from monero_glue.xmr.enc import chacha_poly
from monero_glue.trezor import wrapper as twrap
from monero_glue.messages import MoneroRespError, MoneroTsxSign, \
    MoneroTsxInit, MoneroTsxInitResp, \
    MoneroTsxData, MoneroTsxSetInput, MoneroTsxSetInputResp, \
    MoneroTsxInputsPermutation, MoneroTsxInputsPermutationResp, \
    MoneroTsxInputVini, MoneroTsxInputViniResp, \
    MoneroTsxSetOutput, MoneroTsxSetOutputResp, \
    MoneroTsxAllOutSet, MoneroTsxAllOutSetResp, \
    MoneroTsxMlsagDone, MoneroTsxMlsagDoneResp, \
    MoneroTsxSignInput, MoneroTsxSignInputResp, \
    MoneroTsxFinal, MoneroTsxFinalResp, MoneroRctSig


class TsxSigner(object):
    """
    Monero Transaction signer.
    Provides interface to the host, packages messages.
    """

    def __init__(self, ctx=None, iface=None, creds=None):
        self.ctx = ctx
        self.tsx_ctr = 0
        self.err_ctr = 0
        self.tsx_obj = None  # type: TTransactionBuilder
        self.creds = creds  # type: monero.AccountCreds
        self.iface = iface
        self.debug = True
        self.purge = False

    async def tsx_exc_handler(self, e):
        """
        Handles the exception thrown in the Trezor processing. Clears transaction state.
        We could use decorator/wrapper for message calls but not sure how uPython handles them
        so now are entry points wrapped in try-catch.

        :param e:
        :return:
        """
        if self.debug:
            pass  # traceback.print_exc()

        self.err_ctr += 1
        self.purge = True
        self.tsx_obj = None  # clear transaction object
        await self.iface.transaction_error(e)

    async def should_purge(self):
        """
        Delete global state?
        :return:
        """
        return self.purge or (self.tsx_obj and self.tsx_obj.is_terminal())

    async def setup(self, msg: MoneroTsxInit):
        self.creds = await twrap.monero_get_creds(self.ctx, msg.address_n or (), msg.network_type)

    async def sign(self, ctx, msg: MoneroTsxSign):
        """
        Main multiplex point
        :param ctx:
        :param msg:
        :return:
        """
        self.ctx = ctx
        self.iface = twrap.get_interface(ctx)

        if msg.init:
            await self.setup(msg.init)
            return await self.tsx_init(msg.init.tsx_data)
        elif msg.set_input:
            return await self.tsx_set_input(msg.set_input)
        elif msg.input_permutation:
            return await self.tsx_inputs_permutation(msg.input_permutation)
        elif msg.input_vini:
            return await self.tsx_input_vini(msg.input_vini)
        elif msg.set_output:
            return await self.tsx_set_output1(msg.set_output)
        elif msg.all_out_set:
            return await self.tsx_all_out1_set(msg.all_out_set)
        elif msg.mlsag_done:
            return await self.tsx_mlsag_done()
        elif msg.sign_input:
            return await self.tsx_sign_input(msg.sign_input)
        elif msg.final_msg:
            return await self.tsx_sign_final(msg.final_msg)
        else:
            raise ValueError('Unknown message')

    async def tsx_init(self, tsx_data: MoneroTsxData):
        """
        Initialize transaction state.
        :param tsx_data:
        :return:
        """
        self.tsx_ctr += 1
        self.tsx_obj = TTransactionBuilder(self, creds=self.creds)
        try:
            tsxd = await misc.translate_tsx_data(tsx_data)
            return await self.tsx_obj.init_transaction(tsxd, self.tsx_ctr)
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_set_input(self, msg: MoneroTsxSetInput):
        """
        Sets UTXO one by one.
        Computes spending secret key, key image. tx.vin[i] + HMAC, Pedersen commitment on amount.

        If number of inputs is small, in-memory mode is used = alpha, pseudo_outs are kept in the Trezor.
        Otherwise pseudo_outs are offloaded with HMAC, alpha is offloaded encrypted under AES-GCM() with
        key derived for exactly this purpose.

        :param msg
        :return:
        """
        try:
            src_entr = await misc.parse_src_entry(msg.src_entr)
            return await self.tsx_obj.set_input(src_entr)
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_inputs_permutation(self, msg: MoneroTsxInputsPermutation):
        """
        Set permutation on the inputs - sorted by key image on host.

        :return:
        """
        try:
            return await self.tsx_obj.tsx_inputs_permutation(msg.perm)
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_input_vini(self, msg: MoneroTsxInputVini):
        """
        Set tx.vin[i] for incremental tx prefix hash computation.
        After sorting by key images on host.

        :return:
        """
        try:
            src_entr = await misc.parse_src_entry(msg.src_entr)
            vini = await misc.parse_vini(msg.vini)
            return await self.tsx_obj.input_vini(src_entr, vini, msg.vini_hmac, msg.pseudo_out, msg.pseudo_out_hmac)
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_set_output1(self, msg: MoneroTsxSetOutput):
        """
        Set destination entry one by one.
        Computes destination stealth address, amount key, range proof + HMAC, out_pk, ecdh_info.

        :param msg
        :return:
        """
        try:
            dst_entr = await misc.parse_dst_entry(msg.dst_entr)
            return await self.tsx_obj.set_out1(dst_entr, msg.dst_entr_hmac)
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_all_out1_set(self, msg: MoneroTsxAllOutSet = None):
        """
        All outputs were set in this phase. Computes additional public keys (if needed), tx.extra and
        transaction prefix hash.
        Adds additional public keys to the tx.extra

        :return: tx.extra, tx_prefix_hash
        """
        try:
            return await self.tsx_obj.all_out1_set()

        except misc.TrezorTxPrefixHashNotMatchingError as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(status=10, exc=e)

        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_mlsag_done(self, msg: MoneroTsxMlsagDone = None):
        """
        MLSAG message computed.

        :return:
        """
        try:
            return await self.tsx_obj.mlsag_done()
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_sign_input(self, msg: MoneroTsxSignInput):
        """
        Generates a signature for one input.

        :return:
        """
        try:
            src_entr = await misc.parse_src_entry(msg.src_entr)
            vini = await misc.parse_vini(msg.vini)
            return await self.tsx_obj.sign_input(src_entr, vini, msg.vini_hmac,
                                                 msg.pseudo_out, msg.pseudo_out_hmac, msg.alpha)
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)

    async def tsx_sign_final(self, msg: MoneroTsxFinal = None):
        """
        Final message.
        Offloading tx related data, encrypted.

        :return:
        """
        try:
            return await self.tsx_obj.final_msg()
        except Exception as e:
            await self.tsx_exc_handler(e)
            return MoneroRespError(exc=e)


class TState(object):
    """
    Transaction state
    """
    START = 0
    INIT = 1
    INP_CNT = 2
    INPUT = 3
    INPUT_DONE = 4
    INPUT_PERM = 5
    INPUT_VINS = 6
    OUTPUT = 7
    OUTPUT_DONE = 8
    FINAL_MESSAGE = 9
    SIGNATURE = 10
    SIGNATURE_DONE = 11
    FINAL = 12
    FAIL = 250

    def __init__(self):
        self.s = self.START
        self.in_mem = False

    def init_tsx(self):
        if self.s != self.START:
            raise ValueError('Illegal state')
        self.s = self.INIT

    def inp_cnt(self, in_mem):
        if self.s != self.INIT:
            raise ValueError('Illegal state')
        self.s = self.INP_CNT
        self.in_mem = in_mem

    def input(self):
        if self.s != self.INP_CNT and self.s != self.INPUT:
            raise ValueError('Illegal state')
        self.s = self.INPUT

    def input_done(self):
        if self.s != self.INPUT:
            raise ValueError('Illegal state')
        self.s = self.INPUT_DONE

    def input_permutation(self):
        if self.s != self.INPUT_DONE:
            raise ValueError('Illegal state')
        self.s = self.INPUT_PERM

    def input_vins(self):
        if self.s != self.INPUT_PERM and self.s != self.INPUT_VINS:
            raise ValueError('Illegal state')
        self.s = self.INPUT_VINS

    def is_input_vins(self):
        return self.s == self.INPUT_VINS

    def set_output(self):
        if ((not self.in_mem and self.s != self.INPUT_VINS)
            or (self.in_mem and self.s != self.INPUT_PERM)) \
                and self.s != self.OUTPUT:
            raise ValueError('Illegal state')
        self.s = self.OUTPUT

    def set_output_done(self):
        if self.s != self.OUTPUT:
            raise ValueError('Illegal state')
        self.s = self.OUTPUT_DONE

    def set_final_message_done(self):
        if self.s != self.OUTPUT_DONE:
            raise ValueError('Illegal state')
        self.s = self.FINAL_MESSAGE

    def set_signature(self):
        if self.s != self.FINAL_MESSAGE and self.s != self.SIGNATURE:
            raise ValueError('Illegal state')
        self.s = self.SIGNATURE

    def set_signature_done(self):
        if self.s != self.SIGNATURE:
            raise ValueError('Illegal state')
        self.s = self.SIGNATURE_DONE

    def set_final(self):
        if self.s != self.SIGNATURE_DONE:
            raise ValueError('Illegal state')
        self.s = self.FINAL

    def set_fail(self):
        self.s = self.FAIL

    def is_terminal(self):
        return self.s in [self.FINAL, self.FAIL]


class TTransactionBuilder(object):
    """
    Transaction builder
    """

    STEP_INP = 100
    STEP_PERM = 200
    STEP_VINI = 300
    STEP_OUT = 400
    STEP_ALL_OUT = 500
    STEP_MLSAG = 600
    STEP_SIGN = 700

    def __init__(self, trezor=None, creds=None, **kwargs):
        self.trezor = trezor  # type: TsxSigner
        self.creds = creds  # type: monero.AccountCreds
        self.key_master = None
        self.key_hmac = None
        self.key_enc = None

        self.r = None  # txkey
        self.r_pub = None
        self.state = TState()

        self.multi_sig = False
        self.need_additional_txkeys = False
        self.use_bulletproof = False
        self.use_rct = True
        self.use_simple_rct = False
        self.input_count = 0
        self.output_count = 0
        self.output_change = None
        self.mixin = 0
        self.fee = 0

        self.additional_tx_private_keys = []
        self.additional_tx_public_keys = []
        self.inp_idx = -1
        self.out_idx = -1
        self.summary_inputs_money = 0
        self.summary_outs_money = 0
        self.input_secrets = []
        self.input_alphas = []
        self.input_pseudo_outs = []
        self.output_sk = []
        self.output_pk = []
        self.sumout = crypto.sc_0()
        self.sumpouts_alphas = crypto.sc_0()
        self.subaddresses = {}
        self.tx = xmrtypes.Transaction(vin=[], vout=[], extra=b'')
        self.source_permutation = []  # sorted by key images
        self.tx_prefix_hasher = monero.KeccakArchive()
        self.tx_prefix_hash = None
        self.full_message_hasher = monero.PreMlsagHasher()
        self.full_message = None
        self.exp_tx_prefix_hash = None

    def assrt(self, condition, msg=None):
        """
        Asserts condition
        :param condition:
        :param msg:
        :return:
        """
        if condition:
            return
        raise ValueError('Assertion error%s' % (' : %s' % msg if msg else ''))

    def is_terminal(self):
        """
        Returns true if the state is terminal
        :return:
        """
        return self.state.is_terminal()

    def gen_r(self, use_r=None):
        """
        Generates a new transaction key pair.
        :param use_r:
        :return:
        """
        self.r = crypto.random_scalar() if use_r is None else use_r
        self.r_pub = crypto.scalarmult_base(self.r)

    def check_change(self, outputs):
        """
        Checks if the change address is among tx outputs.
        :param outputs:
        :return:
        """
        change_addr = self.change_address()
        if change_addr is None:
            return

        for out in outputs:
            if out.addr == change_addr:
                return True

        raise ValueError('Change address not found in outputs')

    def in_memory(self):
        """
        Returns true if the input transaction can be processed whole in-memory
        :return:
        """
        return self.input_count <= 1

    def num_inputs(self):
        """
        Number of inputs
        :return:
        """
        return self.input_count

    def num_dests(self):
        """
        Number of destinations
        :return:
        """
        return self.output_count

    def get_fee(self):
        """
        Txn fee
        :return:
        """
        return self.fee if self.fee > 0 else 0

    def change_address(self):
        """
        Returns change address if change dst is set
        :return:
        """
        return self.output_change.addr if self.output_change else None

    def get_rct_type(self):
        """
        RCTsig type (simple/full x Borromean/Bulletproof)
        :return:
        """
        if self.use_simple_rct:
            return xmrtypes.RctType.SimpleBulletproof if self.use_bulletproof else xmrtypes.RctType.Simple
        else:
            return xmrtypes.RctType.FullBulletproof if self.use_bulletproof else xmrtypes.RctType.Full

    def init_rct_sig(self):
        """
        Initializes RCTsig structure (fee, tx prefix hash, type)
        :return:
        """
        rv = xmrtypes.RctSig()
        rv.p = xmrtypes.RctSigPrunable()
        rv.txnFee = self.get_fee()
        rv.message = self.tx_prefix_hash
        rv.type = self.get_rct_type()
        return rv

    def hmac_key_txin(self, idx):
        """
        (TxSourceEntry[i] || tx.vin[i]) hmac key
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_hmac + b'txin' + xmrserialize.dump_uvarint_b(idx))

    def hmac_key_txin_comm(self, idx):
        """
        pseudo_outputs[i] hmac key. Pedersen commitment for inputs.
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_hmac + b'txin-comm' + xmrserialize.dump_uvarint_b(idx))

    def hmac_key_txdst(self, idx):
        """
        TxDestinationEntry[i] hmac key
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_hmac + b'txdest' + xmrserialize.dump_uvarint_b(idx))

    def hmac_key_txout(self, idx):
        """
        (TxDestinationEntry[i] || tx.vout[i]) hmac key
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_hmac + b'txout' + xmrserialize.dump_uvarint_b(idx))

    def hmac_key_txout_asig(self, idx):
        """
        rsig[i] hmac key. Range signature HMAC
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_hmac + b'txout-asig' + xmrserialize.dump_uvarint_b(idx))

    def enc_key_txin_alpha(self, idx):
        """
        AES-GCM encryption key for alpha[i] used in Pedersen commitment in pseudo_outs[i]
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_enc + b'txin-alpha' + xmrserialize.dump_uvarint_b(idx))

    def enc_key_cout(self, idx=None):
        """
        AES-GCM encryption key for multisig C values from MLASG.
        :param idx:
        :return:
        """
        return crypto.keccak_2hash(self.key_enc + b'cout' + (xmrserialize.dump_uvarint_b(idx) if idx else ''))

    async def gen_hmac_vini(self, src_entr, vini, idx):
        """
        Computes hmac (TxSourceEntry[i] || tx.vin[i])
        :param src_entr:
        :param vini:
        :param idx:
        :return:
        """
        kwriter = monero.get_keccak_writer()
        ar = xmrserialize.Archive(kwriter, True)
        await ar.message(src_entr, xmrtypes.TxSourceEntry)
        await ar.message(vini, xmrtypes.TxinToKey)

        hmac_key_vini = self.hmac_key_txin(idx)
        hmac_vini = crypto.compute_hmac(hmac_key_vini, kwriter.get_digest())
        return hmac_vini

    async def gen_hmac_vouti(self, dst_entr, tx_out, idx):
        """
        Generates HMAC for (TxDestinationEntry[i] || tx.vout[i])
        :param dst_entr:
        :param tx_out:
        :param idx:
        :return:
        """
        kwriter = monero.get_keccak_writer()
        ar = xmrserialize.Archive(kwriter, True)
        await ar.message(dst_entr, xmrtypes.TxDestinationEntry)
        await ar.message(tx_out, xmrtypes.TxOut)

        hmac_key_vouti = self.hmac_key_txout(idx)
        hmac_vouti = crypto.compute_hmac(hmac_key_vouti, kwriter.get_digest())
        return hmac_vouti

    async def gen_hmac_tsxdest(self, dst_entr, idx):
        """
        Generates HMAC for TxDestinationEntry[i]
        :param dst_entr:
        :param idx:
        :return:
        """
        kwriter = monero.get_keccak_writer()
        ar = xmrserialize.Archive(kwriter, True)
        await ar.message(dst_entr, xmrtypes.TxDestinationEntry)

        hmac_key = self.hmac_key_txdst(idx)
        hmac_tsxdest = crypto.compute_hmac(hmac_key, kwriter.get_digest())
        return hmac_tsxdest

    async def init_transaction(self, tsx_data, tsx_ctr):
        """
        Initializes a new transaction.
        :param tsx_data:
        :type tsx_data: TsxData
        :param tsx_ctr:
        :return:
        """
        self.gen_r()
        self.state.init_tsx()

        # Ask for confirmation
        confirmation = await self.trezor.iface.confirm_transaction(tsx_data)
        if not confirmation:
            return MoneroRespError(reason='rejected')

        # Basic transaction parameters
        self.input_count = tsx_data.num_inputs
        self.output_count = len(tsx_data.outputs)
        self.output_change = tsx_data.change_dts
        self.mixin = tsx_data.mixin
        self.fee = tsx_data.fee
        self.use_simple_rct = self.input_count > 1
        self.multi_sig = tsx_data.is_multisig
        self.state.inp_cnt(self.in_memory())
        self.check_change(tsx_data.outputs)
        self.exp_tx_prefix_hash = common.defval_empty(tsx_data.exp_tx_prefix_hash, None)

        # Provided tx key, used mostly in multisig.
        if len(tsx_data.use_tx_keys) > 0:
            for ckey in tsx_data.use_tx_keys:
                crypto.check_sc(crypto.decodeint(ckey))

            self.gen_r(use_r=crypto.decodeint(tsx_data.use_tx_keys[0]))
            self.additional_tx_private_keys = [crypto.decodeint(x) for x in tsx_data.use_tx_keys[1:]]

        # Additional keys w.r.t. subaddress destinations
        class_res = classify_subaddresses(tsx_data.outputs, self.change_address())
        num_stdaddresses, num_subaddresses, single_dest_subaddress = class_res

        # if this is a single-destination transfer to a subaddress, we set the tx pubkey to R=s*D
        if num_stdaddresses == 0 and num_subaddresses == 1:
            self.r_pub = crypto.ge_scalarmult(self.r, crypto.decodepoint(single_dest_subaddress.m_spend_public_key))

        self.need_additional_txkeys = num_subaddresses > 0 and (num_stdaddresses > 0 or num_subaddresses > 1)

        # Extra processing, payment id
        self.tx.version = 2
        self.tx.unlock_time = tsx_data.unlock_time
        await self.process_payment_id(tsx_data)
        await self.compute_sec_keys(tsx_data, tsx_ctr)

        # Iterative tx_prefix_hash hash computation
        await self.tx_prefix_hasher.ar.message_field(self.tx, xmrtypes.TransactionPrefix.MFIELDS[0])
        await self.tx_prefix_hasher.ar.message_field(self.tx, xmrtypes.TransactionPrefix.MFIELDS[1])
        await self.tx_prefix_hasher.ar.container_size(self.num_inputs(), xmrtypes.TransactionPrefix.MFIELDS[2][1])

        # Final message hasher
        self.full_message_hasher.init(self.use_simple_rct)
        await self.full_message_hasher.set_type_fee(self.get_rct_type(), self.get_fee())

        # Sub address precomputation
        if tsx_data.account is not None and tsx_data.minor_indices:
            self.precompute_subaddr(tsx_data.account, tsx_data.minor_indices)

        # HMAC outputs - pinning
        hmacs = []
        for idx in range(self.num_dests()):
            c_hmac = await self.gen_hmac_tsxdest(tsx_data.outputs[idx], idx)
            hmacs.append(c_hmac)

        return MoneroTsxInitResp(in_memory=self.in_memory(), hmacs=hmacs)

    async def process_payment_id(self, tsx_data):
        """
        Payment id -> extra
        :return:
        """
        if common.is_empty(tsx_data.payment_id):
            return

        view_key_pub_enc = monero.get_destination_view_key_pub(tsx_data.outputs, self.change_address())
        if view_key_pub_enc == crypto.NULL_KEY_ENC:
            raise ValueError('Destinations have to have exactly one output to support encrypted payment ids')

        view_key_pub = crypto.decodepoint(view_key_pub_enc)
        payment_id_encr = monero.encrypt_payment_id(tsx_data.payment_id, view_key_pub, self.r)

        extra_nonce = monero.set_encrypted_payment_id_to_tx_extra_nonce(payment_id_encr)
        self.tx.extra = monero.add_extra_nonce_to_tx_extra(b'', extra_nonce)

    async def compute_sec_keys(self, tsx_data, tsx_ctr):
        """
        Generate master key H(TsxData || r || c_tsx)
        :return:
        """
        writer = monero.get_keccak_writer()
        ar1 = xmrserialize.Archive(writer, True)
        await ar1.message(tsx_data)
        await writer.awrite(crypto.encodeint(self.r))
        await xmrserialize.dump_uvarint(writer, tsx_ctr)
        self.key_master = crypto.keccak_2hash(writer.get_digest() + crypto.encodeint(crypto.random_scalar()))
        self.key_hmac = crypto.keccak_2hash(b'hmac' + self.key_master)
        self.key_enc = crypto.keccak_2hash(b'enc' + self.key_master)

    def precompute_subaddr(self, account, indices):
        """
        Precomputes subaddresses for account (major) and list of indices (minors)
        Subaddresses have to be stored in encoded form - unique representation.
        Single point can have multiple extended coordinates representation - would not match during subaddress search.
        :param account:
        :param indices:
        :return:
        """
        monero.compute_subaddresses(self.trezor.creds, account, indices, self.subaddresses)

    async def set_input(self, src_entr):
        """
        Sets UTXO one by one.
        Computes spending secret key, key image. tx.vin[i] + HMAC, Pedersen commitment on amount.

        If number of inputs is small, in-memory mode is used = alpha, pseudo_outs are kept in the Trezor.
        Otherwise pseudo_outs are offloaded with HMAC, alpha is offloaded encrypted under AES-GCM() with
        key derived for exactly this purpose.

        :param src_entr:
        :type src_entr: xmrtypes.TxSourceEntry
        :return:
        """
        self.state.input()
        self.inp_idx += 1

        await self.trezor.iface.transaction_step(self.STEP_INP, self.inp_idx)

        if self.inp_idx >= self.num_inputs():
            raise ValueError('Too many inputs')
        if src_entr.real_output >= len(src_entr.outputs):
            raise ValueError(
                'real_output index %s bigger than output_keys.size()' % (src_entr.real_output, len(src_entr.outputs)))
        self.summary_inputs_money += src_entr.amount

        # Secrets derivation
        out_key = crypto.decodepoint(src_entr.outputs[src_entr.real_output][1].dest)
        tx_key = crypto.decodepoint(src_entr.real_out_tx_key)
        additional_keys = [crypto.decodepoint(x) for x in src_entr.real_out_additional_tx_keys]

        secs = monero.generate_key_image_helper(self.trezor.creds, self.subaddresses, out_key,
                                                tx_key,
                                                additional_keys,
                                                src_entr.real_output_in_tx_index)
        xi, ki, di = secs
        self.input_secrets.append(xi)

        # Construct tx.vin
        ki_real = src_entr.multisig_kLRki.ki if self.multi_sig else ki
        vini = xmrtypes.TxinToKey(amount=src_entr.amount, k_image=crypto.encodepoint(ki_real))
        vini.key_offsets = [x[0] for x in src_entr.outputs]
        vini.key_offsets = monero.absolute_output_offsets_to_relative(vini.key_offsets)

        if src_entr.rct:
            vini.amount = 0

        if self.in_memory():
            self.tx.vin.append(vini)

        # HMAC(T_in,i || vin_i)
        hmac_vini = await self.gen_hmac_vini(src_entr, vini, self.inp_idx)

        # PseudoOuts commitment, alphas stored to state
        pseudo_out = None
        pseudo_out_hmac = None
        alpha_enc = None
        if self.use_simple_rct:
            alpha, pseudo_out = await self.commitment(src_entr.amount)
            pseudo_out = crypto.encodepoint(pseudo_out)

            # In full version the alpha is encrypted and passed back for storage
            if self.in_memory():
                self.input_alphas.append(alpha)
                self.input_pseudo_outs.append(pseudo_out)
            else:
                pseudo_out_hmac = crypto.compute_hmac(self.hmac_key_txin_comm(self.inp_idx), pseudo_out)
                alpha_enc = chacha_poly.encrypt_pack(self.enc_key_txin_alpha(self.inp_idx), crypto.encodeint(alpha))

        # All inputs done?
        if self.inp_idx + 1 == self.num_inputs():
            await self.tsx_inputs_done()

        return MoneroTsxSetInputResp(vini=await misc.dump_msg(vini), vini_hmac=hmac_vini,
                                     pseudo_out=pseudo_out, pseudo_out_hmac=pseudo_out_hmac,
                                     alpha_enc=alpha_enc)

    async def tsx_inputs_done(self):
        """
        All inputs set
        :return:
        """
        self.state.input_done()
        if self.inp_idx + 1 != self.num_inputs():
            raise ValueError('Input count mismatch')

        if self.in_memory():
            return await self.tsx_inputs_done_inm()

    async def tsx_inputs_done_inm(self):
        """
        In-memory post processing - tx.vin[i] sorting by key image.
        Used only if number of inputs is small - computable in Trezor without offloading.

        :return:
        """
        # Sort tx.in by key image
        self.source_permutation = list(range(self.num_inputs()))
        self.source_permutation.sort(key=lambda x: self.tx.vin[x].k_image, reverse=True)
        await self._tsx_inputs_permutation(self.source_permutation)

    async def tsx_inputs_permutation(self, permutation):
        """
        Set permutation on the inputs - sorted by key image on host.

        :param permutation:
        :return:
        """
        await self.trezor.iface.transaction_step(self.STEP_PERM)

        if self.in_memory():
            return
        await self._tsx_inputs_permutation(permutation)
        return MoneroTsxInputsPermutationResp()

    async def _tsx_inputs_permutation(self, permutation):
        """
        Set permutation on the inputs - sorted by key image on host.

        :param permutation:
        :return:
        """
        self.state.input_permutation()
        self.source_permutation = permutation

        def swapper(x, y):
            self.input_secrets[x], self.input_secrets[y] = self.input_secrets[y], self.input_secrets[x]
            if self.in_memory() and self.use_simple_rct:
                self.input_alphas[x], self.input_alphas[y] = self.input_alphas[y], self.input_alphas[x]
                self.input_pseudo_outs[x], self.input_pseudo_outs[y] = self.input_pseudo_outs[y], \
                                                                       self.input_pseudo_outs[x]
            if self.in_memory():
                self.tx.vin[x], self.tx.vin[y] = self.tx.vin[y], self.tx.vin[x]

        common.apply_permutation(self.source_permutation, swapper)
        self.inp_idx = -1

        # Incremental hashing
        if self.in_memory():
            for idx in range(self.num_inputs()):
                await self.hash_vini_pseudo_out(self.tx.vin[idx], idx)

    async def input_vini(self, src_entr, vini, hmac, pseudo_out, pseudo_out_hmac):
        """
        Set tx.vin[i] for incremental tx prefix hash computation.
        After sorting by key images on host.
        Hashes pseudo_out to the final_message.

        :param src_entr:
        :param vini: tx.vin[i]
        :param hmac: HMAC of tx.vin[i]
        :param pseudo_out: pseudo_out for the current entry
        :param pseudo_out_hmac: hmac of pseudo_out
        :return:
        """
        await self.trezor.iface.transaction_step(self.STEP_VINI, self.inp_idx + 1)

        if self.in_memory():
            return
        if self.inp_idx >= self.num_inputs():
            raise ValueError('Too many inputs')

        self.state.input_vins()
        self.inp_idx += 1

        # HMAC(T_in,i || vin_i)
        hmac_vini = await self.gen_hmac_vini(src_entr, vini, self.source_permutation[self.inp_idx])
        if not common.ct_equal(hmac_vini, hmac):
            raise ValueError('HMAC is not correct')

        await self.hash_vini_pseudo_out(vini, self.inp_idx, pseudo_out, pseudo_out_hmac)
        return MoneroTsxInputViniResp()

    async def hash_vini_pseudo_out(self, vini, inp_idx, pseudo_out=None, pseudo_out_hmac=None):
        """
        Incremental hasing of tx.vin[i] and pseudo output
        :param vini:
        :param inp_idx:
        :param pseudo_out:
        :param pseudo_out_hmac:
        :return:
        """
        # Serialize particular input type
        await self.tx_prefix_hasher.ar.field(vini, xmrtypes.TxInV)

        # Pseudo_out incremental hashing - applicable only in simple rct
        if not self.use_simple_rct:
            return

        if not self.in_memory():
            idx = self.source_permutation[inp_idx]
            pseudo_out_hmac_comp = crypto.compute_hmac(self.hmac_key_txin_comm(idx), pseudo_out)
            if not common.ct_equal(pseudo_out_hmac, pseudo_out_hmac_comp):
                raise ValueError('HMAC invalid for pseudo outs')
        else:
            pseudo_out = self.input_pseudo_outs[inp_idx]

        await self.full_message_hasher.set_pseudo_out(pseudo_out)

    async def commitment(self, in_amount):
        """
        Computes Pedersen commitment - pseudo outs
        Here is slight deviation from the original protocol.
        We want that \sum Alpha = \sum A_{i,j} where A_{i,j} is a mask from range proof for output i, bit j.

        Previously this was computed in such a way that Alpha_{last} = \sum A{i,j} - \sum_{i=0}^{last-1} Alpha
        But we would prefer to compute commitment before range proofs so alphas are generated completely randomly
        and the last A mask is computed in this special way.
        Returns pseudo_out
        :return:
        """
        alpha = crypto.random_scalar()
        self.sumpouts_alphas = crypto.sc_add(self.sumpouts_alphas, alpha)
        return alpha, crypto.gen_c(alpha, in_amount)

    async def range_proof(self, idx, dest_pub_key, amount, amount_key):
        """
        Computes rangeproof and related information - out_sk, out_pk, ecdh_info.
        In order to optimize incremental transaction build, the mask computation is changed compared
        to the official Monero code. In the official code, the input pedersen commitments are computed
        after range proof in such a way summed masks for commitments (alpha) and rangeproofs (ai) are equal.

        In order to save roundtrips we compute commitments randomly and then for the last rangeproof
        a[63] = (\sum_{i=0}^{num_inp}alpha_i - \sum_{i=0}^{num_outs-1} amasks_i) - \sum_{i=0}^{62}a_i

        The range proof is incrementally hashed to the final_message.

        :param idx:
        :param dest_pub_key:
        :param amount:
        :param amount_key:
        :return:
        """
        out_pk = xmrtypes.CtKey(dest=dest_pub_key)
        is_last = idx + 1 == self.num_dests()
        last_mask = None if not is_last or not self.use_simple_rct else crypto.sc_sub(self.sumpouts_alphas, self.sumout)

        # Pedersen commitment on the value, mask from the commitment, range signature.
        C, mask, rsig = None, 0, None

        # Rangeproof
        if self.use_bulletproof:
            raise ValueError('Bulletproof not yet supported')

        else:
            C, mask, rsig = ring_ct.prove_range(amount, last_mask, backend_impl=True, byte_enc=True)

            if __debug__:
                rsig_bytes = monero.inflate_rsig(rsig)
                self.assrt(ring_ct.ver_range(C, rsig_bytes))
                self.assrt(crypto.point_eq(C, crypto.point_add(
                    crypto.scalarmult_base(mask),
                    crypto.scalarmult_h(amount))))

            # Incremental hashing
            await self.full_message_hasher.rsig_val(rsig, self.use_bulletproof, raw=True)

        # Mask sum
        out_pk.mask = crypto.encodepoint(C)
        self.sumout = crypto.sc_add(self.sumout, mask)
        self.output_sk.append(xmrtypes.CtKey(mask=mask))

        # ECDH masking
        ecdh_info = xmrtypes.EcdhTuple(mask=mask, amount=crypto.sc_init(amount))
        ecdh_info = ring_ct.ecdh_encode(ecdh_info, derivation=crypto.encodeint(amount_key))
        monero.recode_ecdh(ecdh_info, encode=True)
        return rsig, out_pk, ecdh_info

    async def set_out1(self, dst_entr, dst_entr_hmac):
        """
        Set destination entry one by one.
        Computes destination stealth address, amount key, range proof + HMAC, out_pk, ecdh_info.

        :param dst_entr
        :type dst_entr: xmrtypes.TxDestinationEntry
        :param dst_entr_hmac
        :return:
        """
        await self.trezor.iface.transaction_step(self.STEP_OUT, self.out_idx + 1)

        if self.state.is_input_vins() and self.inp_idx + 1 != self.num_inputs():
            raise ValueError('Invalid number of inputs')

        self.state.set_output()
        self.out_idx += 1
        change_addr = self.change_address()

        if dst_entr.amount <= 0 and self.tx.version <= 1:
            raise ValueError('Destination with wrong amount: %s' % dst_entr.amount)

        # HMAC check of the destination
        dst_entr_hmac_computed = await self.gen_hmac_tsxdest(dst_entr, self.out_idx)
        if not common.ct_equal(dst_entr_hmac, dst_entr_hmac_computed):
            raise ValueError('HMAC invalid')

        # First output - tx prefix hasher - size of the container
        if self.out_idx == 0:
            await self.tx_prefix_hasher.ar.container_size(self.num_dests(), xmrtypes.TransactionPrefix.MFIELDS[3][1])

        additional_txkey = None
        additional_txkey_priv = None
        if self.need_additional_txkeys:
            use_provided = self.num_dests() == len(self.additional_tx_private_keys)
            additional_txkey_priv = self.additional_tx_private_keys[
                self.out_idx] if use_provided else crypto.random_scalar()

            if dst_entr.is_subaddress:
                additional_txkey = crypto.ge_scalarmult(additional_txkey_priv,
                                                        crypto.decodepoint(dst_entr.addr.m_spend_public_key))
            else:
                additional_txkey = crypto.ge_scalarmult_base(additional_txkey_priv)

            self.additional_tx_public_keys.append(crypto.encodepoint(additional_txkey))
            if not use_provided:
                self.additional_tx_private_keys.append(additional_txkey_priv)

        if change_addr and dst_entr.addr == change_addr:
            # sending change to yourself; derivation = a*R
            derivation = monero.generate_key_derivation(self.r_pub, self.creds.view_key_private)

        else:
            # sending to the recipient; derivation = r*A (or s*C in the subaddress scheme)
            deriv_priv = additional_txkey_priv if dst_entr.is_subaddress and self.need_additional_txkeys else self.r
            derivation = monero.generate_key_derivation(crypto.decodepoint(dst_entr.addr.m_view_public_key), deriv_priv)

        amount_key = crypto.derivation_to_scalar(derivation, self.out_idx)
        tx_out_key = crypto.derive_public_key(derivation, self.out_idx,
                                              crypto.decodepoint(dst_entr.addr.m_spend_public_key))
        tk = xmrtypes.TxoutToKey(key=crypto.encodepoint(tx_out_key))
        tx_out = xmrtypes.TxOut(amount=0, target=tk)
        self.summary_outs_money += dst_entr.amount

        # Tx header prefix hashing
        await self.tx_prefix_hasher.ar.field(tx_out, xmrtypes.TxOut)

        # Hmac dest_entr.
        hmac_vouti = await self.gen_hmac_vouti(dst_entr, tx_out, self.out_idx)

        # Range proof, out_pk, ecdh_info
        rsig, out_pk, ecdh_info = await self.range_proof(self.out_idx, dest_pub_key=tk.key, amount=dst_entr.amount,
                                                         amount_key=amount_key)

        # Incremental hashing of the ECDH info.
        # RctSigBase allows to hash only one of the (ecdh, out_pk) as they are serialized
        # as whole vectors. Hashing ECDH info saves state space.
        await self.full_message_hasher.set_ecdh(ecdh_info)

        # Output_pk is stored to the state as it is used during the signature and hashed to the
        # RctSigBase later.
        self.output_pk.append(out_pk)
        return MoneroTsxSetOutputResp(tx_out=await misc.dump_msg(tx_out),
                                      vouti_hmac=hmac_vouti, rsig=rsig,  # rsig is already byte-encoded
                                      out_pk=await misc.dump_msg(out_pk),
                                      ecdh_info=await misc.dump_msg(ecdh_info))

    async def all_out1_set(self):
        """
        All outputs were set in this phase. Computes additional public keys (if needed), tx.extra and
        transaction prefix hash.
        Adds additional public keys to the tx.extra

        :return: tx.extra, tx_prefix_hash
        """
        self.state.set_output_done()
        await self.trezor.iface.transaction_step(self.STEP_ALL_OUT)

        if self.out_idx + 1 != self.num_dests():
            raise ValueError('Invalid out num')

        # Test if \sum Alpha == \sum A
        if self.use_simple_rct:
            self.assrt(crypto.sc_eq(self.sumout, self.sumpouts_alphas))

        # Fee test
        if self.fee != (self.summary_inputs_money - self.summary_outs_money):
            raise ValueError('Fee invalid')

        # Set public key to the extra
        # Not needed to remove - extra is clean
        # self.tx.extra = await monero.remove_field_from_tx_extra(self.tx.extra, xmrtypes.TxExtraPubKey)
        self.tx.extra = monero.add_tx_pub_key_to_extra(self.tx.extra, self.r_pub)

        # Not needed to remove - extra is clean
        # self.tx.extra = await monero.remove_field_from_tx_extra(self.tx.extra, xmrtypes.TxExtraAdditionalPubKeys)
        if self.need_additional_txkeys:
            self.tx.extra = await monero.add_additional_tx_pub_keys_to_extra(self.tx.extra,
                                                                             pub_enc=self.additional_tx_public_keys)

        if self.summary_outs_money > self.summary_inputs_money:
            raise ValueError('Transaction inputs money (%s) less than outputs money (%s)'
                             % (self.summary_inputs_money, self.summary_outs_money))

        # Hashing transaction prefix
        await self.tx_prefix_hasher.ar.message_field(self.tx, xmrtypes.TransactionPrefixExtraBlob.MFIELDS[4])  # extra

        self.tx_prefix_hash = self.tx_prefix_hasher.kwriter.get_digest()
        del self.tx_prefix_hasher

        # Hash message to the final_message
        await self.full_message_hasher.set_message(self.tx_prefix_hash)
        rv = self.init_rct_sig()

        # Txprefix match check for multisig
        if not common.is_empty(self.exp_tx_prefix_hash) and \
                not common.ct_equal(self.exp_tx_prefix_hash, self.tx_prefix_hash):
            self.state.set_fail()
            raise misc.TrezorTxPrefixHashNotMatchingError()

        rv_pb = MoneroRctSig(txn_fee=rv.txnFee, message=rv.message, rv_type=rv.type)
        return MoneroTsxAllOutSetResp(extra=self.tx.extra, tx_prefix_hash=self.tx_prefix_hash, rv=rv_pb)

    async def tsx_mlsag_ecdh_info(self):
        """
        Sets ecdh info for the incremental hashing mlsag.

        :return:
        """
        pass

    async def tsx_mlsag_out_pk(self):
        """
        Sets out_pk for the incremental hashing mlsag.

        :return:
        """
        if self.num_dests() != len(self.output_pk):
            raise ValueError('Invalid number of ecdh')

        for out in self.output_pk:
            await self.full_message_hasher.set_out_pk(out)

    async def mlsag_done(self):
        """
        MLSAG message computed.

        :return:
        """
        self.state.set_final_message_done()
        await self.trezor.iface.transaction_step(self.STEP_MLSAG)

        await self.tsx_mlsag_ecdh_info()
        await self.tsx_mlsag_out_pk()
        await self.full_message_hasher.rctsig_base_done()
        self.out_idx = -1
        self.inp_idx = -1

        self.full_message = await self.full_message_hasher.get_digest()
        del self.full_message_hasher

        return MoneroTsxMlsagDoneResp(full_message_hash=self.full_message)

    async def sign_input(self, src_entr, vini, hmac_vini, pseudo_out, pseudo_out_hmac, alpha):
        """
        Generates a signature for one input.

        :param src_entr: Source entry
        :type src_entr: xmrtypes.TxSourceEntry
        :param vini: tx.vin[i] for the transaction. Contains key image, offsets, amount (usually zero)
        :param hmac_vini: HMAC for the tx.vin[i] as returned from Trezor
        :param pseudo_out: pedersen commitment for the current input, uses alpha as the mask.
        Only in memory offloaded scenario. Tuple containing HMAC, as returned from the Trezor.
        :param pseudo_out_hmac:
        :param alpha: alpha mask for the current input. Only in memory offloaded scenario,
        tuple as returned from the Trezor
        :return: Generated signature MGs[i]
        """
        self.state.set_signature()
        await self.trezor.iface.transaction_step(self.STEP_SIGN)

        self.inp_idx += 1
        if self.inp_idx >= self.num_inputs():
            raise ValueError('Invalid ins')
        if not self.in_memory() and alpha is None:
            raise ValueError('Inconsistent')
        if not self.in_memory() and pseudo_out is None:
            raise ValueError('Inconsistent')
        if self.inp_idx >= 1 and not self.use_simple_rct:
            raise ValueError('Inconsistent')

        inv_idx = self.source_permutation[self.inp_idx]

        # Check HMAC of all inputs
        hmac_vini_comp = await self.gen_hmac_vini(src_entr, vini, inv_idx)
        if not common.ct_equal(hmac_vini_comp, hmac_vini):
            raise ValueError('HMAC is not correct')

        if not self.in_memory():
            pseudo_out_hmac_comp = crypto.compute_hmac(self.hmac_key_txin_comm(inv_idx), pseudo_out)
            if not common.ct_equal(pseudo_out_hmac_comp, pseudo_out_hmac):
                raise ValueError('HMAC is not correct')

            alpha_c = chacha_poly.decrypt_pack(self.enc_key_txin_alpha(inv_idx), bytes(alpha))
            alpha_c = crypto.decodeint(alpha_c)
            pseudo_out_c = crypto.decodepoint(pseudo_out)

        elif self.use_simple_rct:
            alpha_c = self.input_alphas[self.inp_idx]
            pseudo_out_c = crypto.decodepoint(self.input_pseudo_outs[self.inp_idx])

        # Basic setup, sanity check
        index = src_entr.real_output
        in_sk = xmrtypes.CtKey(dest=self.input_secrets[self.inp_idx], mask=crypto.decodeint(src_entr.mask))
        kLRki = src_entr.multisig_kLRki if self.multi_sig else None

        # Private key correctness test
        self.assrt(crypto.point_eq(crypto.decodepoint(src_entr.outputs[src_entr.real_output][1].dest),
                                   crypto.scalarmult_base(in_sk.dest)))
        self.assrt(crypto.point_eq(crypto.decodepoint(src_entr.outputs[src_entr.real_output][1].mask),
                                   crypto.gen_c(in_sk.mask, src_entr.amount)))

        # RCT signature
        mg = None
        if self.use_simple_rct:
            # Simple RingCT
            mix_ring = []
            for idx2, out in enumerate(src_entr.outputs):
                mix_ring.append(out[1])

            mg, msc = mlsag2.prove_rct_mg_simple(self.full_message, mix_ring,
                                                 in_sk, alpha_c, pseudo_out_c, kLRki, None, index)

            if __debug__:
                self.assrt(mlsag2.ver_rct_mg_simple(self.full_message, mg, mix_ring, pseudo_out_c))

        else:
            # Full RingCt, only one input
            txn_fee_key = crypto.scalarmult_h(self.get_fee())
            n_total_outs = len(src_entr.outputs)
            mix_ring = [None] * n_total_outs
            for idx in range(n_total_outs):
                mix_ring[idx] = [src_entr.outputs[idx][1]]

            mg, msc = mlsag2.prove_rct_mg(self.full_message, mix_ring,
                                          [in_sk], self.output_sk, self.output_pk, kLRki, None, index, txn_fee_key)

            if __debug__:
                self.assrt(mlsag2.ver_rct_mg(mg, mix_ring, self.output_pk, txn_fee_key, self.full_message))

        # Encode
        mgs = monero.recode_msg([mg])
        cout = None

        # Multisig values returned encrypted, keys returned after finished successfully.
        if self.multi_sig:
            cout = chacha_poly.encrypt(self.enc_key_cout(), crypto.encodeint(msc))

        # Final state transition
        if self.inp_idx + 1 == self.num_inputs():
            self.state.set_signature_done()
            await self.trezor.iface.transaction_signed()

        return MoneroTsxSignInputResp(signature=await misc.dump_msg(mgs[0]), cout=cout)

    async def final_msg(self, *args, **kwargs):
        """
        Final step after transaction signing.

        :param args:
        :param kwargs:
        :return:
        """
        self.state.set_final()

        cout_key = self.enc_key_cout() if self.multi_sig else None

        # Encrypted tx keys under transaction specific key, derived from txhash and spend key.
        # Deterministic transaction key, so we can recover it just from transaction and the spend key.
        tx_key, salt, rand_mult = misc.compute_tx_key(self.creds.spend_key_private, self.tx_prefix_hash)

        key_buff = crypto.encodeint(self.r) + b''.join([crypto.encodeint(x) for x in self.additional_tx_private_keys])
        tx_enc_keys = chacha_poly.encrypt(tx_key, key_buff)

        return MoneroTsxFinalResp(cout_key=cout_key, salt=salt, rand_mult=rand_mult,
                                  tx_enc_keys=b''.join(list(tx_enc_keys)))


