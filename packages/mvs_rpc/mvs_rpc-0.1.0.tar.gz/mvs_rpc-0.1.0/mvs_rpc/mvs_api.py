# -*- coding: utf-8 -*-
from common import mvs_api_v2

@mvs_api_v2
def didchangeaddress(ACCOUNTNAME, ACCOUNTAUTH, TOADDRESS, DIDSYMBOL, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TOADDRESS(str): "Target address"
    :param: DIDSYMBOL(str): "Did symbol"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TOADDRESS, DIDSYMBOL]

    optional = {
        "fee": fee,
    }
    return 'didchangeaddress', positional, optional


@mvs_api_v2
def signmultisigtx(ACCOUNTNAME, ACCOUNTAUTH, TRANSACTION, selfpublickey=None, broadcast=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TRANSACTION(str): "The input Base16 transaction to sign."
    :param: selfpublickey(str): "The private key of this public key will be used to sign."
    :param: broadcast(bool): "Broadcast the tx if it is fullly signed, disabled by default."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TRANSACTION]
    if broadcast == True: positional.append("--broadcast")
    optional = {
        "selfpublickey": selfpublickey,
    }
    return 'signmultisigtx', positional, optional


@mvs_api_v2
def registerdid(ACCOUNTNAME, ACCOUNTAUTH, ADDRESS, SYMBOL, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: ADDRESS(str): "The address will be bound to, can change to other addresses later."
    :param: SYMBOL(str): "The symbol of global unique MVS Digital Identity Destination/Index, supports alphabets/numbers/(“@”, “.”, “_”, “-“), case-sensitive, maximum length is 64."
    :param: fee(int): "The fee of tx. defaults to 1 etp."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, ADDRESS, SYMBOL]

    optional = {
        "fee": fee,
    }
    return 'registerdid', positional, optional


@mvs_api_v2
def issue(ACCOUNTNAME, ACCOUNTAUTH, SYMBOL, model=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: SYMBOL(str): "The asset symbol, global uniqueness, only supports UPPER-CASE alphabet and dot(.)"
    :param: model(str): The token offering model by block height.
    TYPE=1 - fixed quantity model; TYPE=2 - specify parameters;
    LQ - Locked Quantity each period;
    LP - Locked Period, numeber of how many blocks;
    UN - Unlock Number, number of how many LPs;
    eg:
        TYPE=1;LQ=9000;LP=60000;UN=3
        TYPE=2;LQ=9000;LP=60000;UN=3;UC=20000,20000,20000;UQ=3000,3000,3000
    defaults to disable.
    :param: fee(int): "The fee of tx. minimum is 10 etp."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, SYMBOL]

    optional = {
        "model": model,
        "fee": fee,
    }
    return 'issue', positional, optional


@mvs_api_v2
def importaccount(WORD, accountname, password, language=None, hd_index=None):
    '''
    :param: WORD([str1, str2, ...]): "The set of words that that make up the mnemonic. If not specified the words are read from STDIN."
    :param: language(string of hexcode): "The language identifier of the dictionary of the mnemonic. Options are 'en', 'es', 'ja', 'zh_Hans', 'zh_Hant' and 'any', defaults to 'any'."
    :param: accountname(str): Account name required.
    :param: password(str): Account password(authorization) required.
    :param: hd_index(int): "The HD index for the account."
    '''
    positional = [' '.join(WORD)]

    optional = {
        "language": language,
        "accountname": accountname,
        "password": password,
        "hd_index": hd_index,
    }
    return 'importaccount', positional, optional


@mvs_api_v2
def stopmining(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'stopmining', positional, optional


@mvs_api_v2
def createmultisigtx(ACCOUNTNAME, ACCOUNTAUTH, FROMADDRESS, TOADDRESS, AMOUNT, symbol=None, type_=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: FROMADDRESS(str): "Send from this address, must be a multi-signature script address."
    :param: TOADDRESS(str): "Send to this address"
    :param: AMOUNT(int): "ETP integer bits."
    :param: symbol(str): "asset name, not specify this option for etp tx"
    :param: type_(int): "Transaction type, defaults to 0. 0 -- transfer etp, 3 -- transfer asset"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, FROMADDRESS, TOADDRESS, AMOUNT]

    optional = {
        "symbol": symbol,
        "type": type_,
        "fee": fee,
    }
    return 'createmultisigtx', positional, optional


@mvs_api_v2
def getpublickey(ACCOUNTNAME, ACCOUNTAUTH, ADDRESS):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: ADDRESS(str): "Address."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, ADDRESS]

    optional = {

    }
    return 'getpublickey', positional, optional


@mvs_api_v2
def deposit(ACCOUNTNAME, ACCOUNTAUTH, AMOUNT, address=None, deposit=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: AMOUNT(int): "ETP integer bits."
    :param: address(str): "The deposit target address."
    :param: deposit(int): "Deposits support [7, 30, 90, 182, 365] days. defaluts to 7 days"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, AMOUNT]

    optional = {
        "address": address,
        "deposit": deposit,
        "fee": fee,
    }
    return 'deposit', positional, optional


@mvs_api_v2
def getaccountasset(ACCOUNTNAME, ACCOUNTAUTH, SYMBOL=None, cert=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: SYMBOL(str): "Asset symbol."
    :param: cert(bool): "If specified, then only get related asset cert. Default is not specified."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, SYMBOL]
    if cert == True: positional.append("--cert")
    optional = {

    }
    return 'getaccountasset', positional, optional


@mvs_api_v2
def didsendasset(ACCOUNTNAME, ACCOUNTAUTH, TO_, ASSET, AMOUNT, model=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TO_(str): "Asset receiver did/address."
    :param: ASSET(str): "Asset MST symbol."
    :param: AMOUNT(int): "Asset integer bits. see asset <decimal_number>."
    :param: model(str): The token offering model by block height.
    TYPE=1 - fixed quantity model; TYPE=2 - specify parameters;
    LQ - Locked Quantity each period;
    LP - Locked Period, numeber of how many blocks;
    UN - Unlock Number, number of how many LPs;
    eg:
        TYPE=1;LQ=9000;LP=60000;UN=3
        TYPE=2;LQ=9000;LP=60000;UN=3;UC=20000,20000,20000;UQ=3000,3000,3000
    defaults to disable.
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TO_, ASSET, AMOUNT]

    optional = {
        "model": model,
        "fee": fee,
    }
    return 'didsendasset', positional, optional


@mvs_api_v2
def burn(ACCOUNTNAME, ACCOUNTAUTH, SYMBOL, AMOUNT):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: SYMBOL(str): "The asset will be burned."
    :param: AMOUNT(int): "Asset integer bits. see asset <decimal_number>."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, SYMBOL, AMOUNT]

    optional = {

    }
    return 'burn', positional, optional


@mvs_api_v2
def popblock(height):
    '''
    :param: height(int): "specify the starting point to pop out blocks. eg, if specified 1000000, then all blocks with height greater than or equal to 1000000 will be poped out."
    '''
    positional = [height]

    optional = {

    }
    return 'popblock', positional, optional


@mvs_api_v2
def listbalances(ACCOUNTNAME, ACCOUNTAUTH, nozero=None, greater_equal=None, lesser_equal=None):
    '''
    :param: nozero(bool): "Defaults to false."
    :param: greater_equal(int): "Greater than ETP bits."
    :param: lesser_equal(int): "Lesser than ETP bits."
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]
    if nozero == True: positional.append("--nozero")
    optional = {
        "greater_equal": greater_equal,
        "lesser_equal": lesser_equal,
    }
    return 'listbalances', positional, optional


@mvs_api_v2
def createasset(ACCOUNTNAME, ACCOUNTAUTH, symbol, issuer, volume, rate=None, decimalnumber=None, description=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: rate(int): "The percent threshold value when you secondary issue.              0,  not allowed to secondary issue;              -1,  the asset can be secondary issue freely;             [1, 100], the asset can be secondary issue when own percentage greater than or equal to this value.             Defaults to 0."
    :param: symbol(str): "The asset symbol, global uniqueness, only supports UPPER-CASE alphabet and dot(.), eg: CHENHAO.LAPTOP, dot separates prefix 'CHENHAO', It's impossible to create any asset named with 'CHENHAO' prefix, but this issuer."
    :param: issuer(str): "Issue must be specified as a DID symbol."
    :param: volume(int): "The asset maximum supply volume, with unit of integer bits."
    :param: decimalnumber(int): "The asset amount decimal number, defaults to 0."
    :param: description(str): "The asset data chuck, defaults to empty string."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "rate": rate,
        "symbol": symbol,
        "issuer": issuer,
        "volume": volume,
        "decimalnumber": decimalnumber,
        "description": description,
    }
    return 'createasset', positional, optional


@mvs_api_v2
def send(ACCOUNTNAME, ACCOUNTAUTH, TOADDRESS, AMOUNT, memo=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TOADDRESS(str): "Send to this address"
    :param: AMOUNT(int): "ETP integer bits."
    :param: memo(str): "Attached memo for this transaction."
    :param: fee(int): "Transaction fee. defaults to 10000 etp bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TOADDRESS, AMOUNT]

    optional = {
        "memo": memo,
        "fee": fee,
    }
    return 'send', positional, optional


@mvs_api_v2
def changepasswd(ACCOUNTNAME, ACCOUNTAUTH, password):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: password(str): "The new password."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "password": password,
    }
    return 'changepasswd', positional, optional


@mvs_api_v2
def createrawtx(type_, senders, receivers, symbol=None, deposit=None, mychange=None, message=None, fee=None):
    '''
    :param: type_(int): "Transaction type. 0 -- transfer etp, 1 -- deposit etp, 3 -- transfer asset"
    :param: senders([str1, str2, ...]): "Send from addresses"
    :param: receivers([str1, str2, ...]): "Send to [address:amount]. amount is asset number if sybol option specified"
    :param: symbol(str): "asset name, not specify this option for etp tx"
    :param: deposit(int): "Deposits support [7, 30, 90, 182, 365] days. defaluts to 7 days"
    :param: mychange(str): "Mychange to this address, includes etp and asset change"
    :param: message(str): "Message/Information attached to this transaction"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = []

    optional = {
        "type": type_,
        "senders": senders,
        "receivers": receivers,
        "symbol": symbol,
        "deposit": deposit,
        "mychange": mychange,
        "message": message,
        "fee": fee,
    }
    return 'createrawtx', positional, optional


@mvs_api_v2
def validateaddress(PAYMENT_ADDRESS=None):
    '''
    :param: PAYMENT_ADDRESS(str): "Valid payment address. If not specified the address is read from STDIN."
    '''
    positional = [PAYMENT_ADDRESS]

    optional = {

    }
    return 'validateaddress', positional, optional


@mvs_api_v2
def sendfrom(ACCOUNTNAME, ACCOUNTAUTH, FROMADDRESS, TOADDRESS, AMOUNT, memo=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: FROMADDRESS(str): "Send from this address"
    :param: TOADDRESS(str): "Send to this address"
    :param: AMOUNT(int): "ETP integer bits."
    :param: memo(str): "The memo to descript transaction"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, FROMADDRESS, TOADDRESS, AMOUNT]

    optional = {
        "memo": memo,
        "fee": fee,
    }
    return 'sendfrom', positional, optional


@mvs_api_v2
def deletemultisig(ACCOUNTNAME, ACCOUNTAUTH, ADDRESS):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: ADDRESS(str): "The multisig script corresponding address."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, ADDRESS]

    optional = {

    }
    return 'deletemultisig', positional, optional


@mvs_api_v2
def listdids(ACCOUNTNAME=None, ACCOUNTAUTH=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {

    }
    return 'listdids', positional, optional


@mvs_api_v2
def getheight(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'getheight', positional, optional


@mvs_api_v2
def didsend(ACCOUNTNAME, ACCOUNTAUTH, TO_, AMOUNT, memo=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TO_(str): "Send to this did/address"
    :param: AMOUNT(int): "ETP integer bits."
    :param: memo(str): "Attached memo for this transaction."
    :param: fee(int): "Transaction fee. defaults to 10000 etp bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TO_, AMOUNT]

    optional = {
        "memo": memo,
        "fee": fee,
    }
    return 'didsend', positional, optional


@mvs_api_v2
def transfercert(ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, CERT, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TODID(str): "Target did"
    :param: SYMBOL(str): "Asset cert symbol"
    :param: CERT(str): "Asset cert type name. eg. ISSUE, DOMAIN or NAMING"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, CERT]

    optional = {
        "fee": fee,
    }
    return 'transfercert', positional, optional


@mvs_api_v2
def sendrawtx(TRANSACTION, fee=None):
    '''
    :param: TRANSACTION(str): "The input Base16 transaction to broadcast."
    :param: fee(int): "The max tx fee. default_value 10 etp"
    '''
    positional = [TRANSACTION]

    optional = {
        "fee": fee,
    }
    return 'sendrawtx', positional, optional


@mvs_api_v2
def issuecert(ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, CERT, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TODID(str): "The DID will own this cert."
    :param: SYMBOL(str): "Asset Cert Symbol/Name."
    :param: CERT(str): "Asset cert type name can be: ISSUE: cert of issuing asset, generated by issuing asset and used in secondaryissue asset.  DOMAIN: cert of domain, generated by issuing asset, the symbol is same as asset symbol(if it does not contain dot) or the prefix part(that before the first dot) of asset symbol. NAMING: cert of naming right of domain. The owner of domain cert can issue this type of cert by issuecert with symbol like “domain.XYZ”(domain is the symbol of domain cert)."
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, CERT]

    optional = {
        "fee": fee,
    }
    return 'issuecert', positional, optional


@mvs_api_v2
def fetchheaderext(ACCOUNTNAME, ACCOUNTAUTH, NUMBER):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: NUMBER(str): "Block number, or earliest, latest or pending"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, NUMBER]

    optional = {

    }
    return 'fetchheaderext', positional, optional


@mvs_api_v2
def didsendassetfrom(ACCOUNTNAME, ACCOUNTAUTH, FROM_, TO_, SYMBOL, AMOUNT, model=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: FROM_(str): "From did/address"
    :param: TO_(str): "Target did/address"
    :param: SYMBOL(str): "Asset symbol"
    :param: AMOUNT(int): "Asset integer bits. see asset <decimal_number>."
    :param: model(str): The token offering model by block height.
    TYPE=1 - fixed quantity model; TYPE=2 - specify parameters;
    LQ - Locked Quantity each period;
    LP - Locked Period, numeber of how many blocks;
    UN - Unlock Number, number of how many LPs;
    eg:
        TYPE=1;LQ=9000;LP=60000;UN=3
        TYPE=2;LQ=9000;LP=60000;UN=3;UC=20000,20000,20000;UQ=3000,3000,3000
    defaults to disable.
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, FROM_, TO_, SYMBOL, AMOUNT]

    optional = {
        "model": model,
        "fee": fee,
    }
    return 'didsendassetfrom', positional, optional


@mvs_api_v2
def didsendmore(ACCOUNTNAME, ACCOUNTAUTH, receivers, mychange=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: receivers([str1, str2, ...]): "Send to [did/address:etp_bits]."
    :param: mychange(str): "Mychange to this did/address"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "receivers": receivers,
        "mychange": mychange,
        "fee": fee,
    }
    return 'didsendmore', positional, optional


@mvs_api_v2
def sendmore(ACCOUNTNAME, ACCOUNTAUTH, receivers, mychange=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: receivers([str1, str2, ...]): "Send to [address:etp_bits]."
    :param: mychange(str): "Mychange to this address"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "receivers": receivers,
        "mychange": mychange,
        "fee": fee,
    }
    return 'sendmore', positional, optional


@mvs_api_v2
def deletelocalasset(ACCOUNTNAME, ACCOUNTAUTH, symbol):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: symbol(str): "The asset symbol/name. Global unique."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "symbol": symbol,
    }
    return 'deletelocalasset', positional, optional


@mvs_api_v2
def listtxs(ACCOUNTNAME, ACCOUNTAUTH, address=None, height=(0, 0), symbol=None, limit=None, index=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: address(str): "Address."
    :param: height((int_low, int_high)): "Get tx according height eg: -e start-height:end-height will return tx between [start-height, end-height)"
    :param: symbol(str): "Asset symbol."
    :param: limit(int): "Transaction count per page."
    :param: index(int): "Page index."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "address": address,
        "height": "%s:%s" % (height[0], height[1]),
        "symbol": symbol,
        "limit": limit,
        "index": index,
    }
    return 'listtxs', positional, optional


@mvs_api_v2
def getmit(SYMBOL=None, trace=None, limit=None, index=None, current=None):
    '''
    :param: SYMBOL(str): "Asset symbol. If not specified then show whole network MIT symbols."
    :param: trace(bool): "If specified then trace the history. Default is not specified."
    :param: limit(int): "MIT count per page."
    :param: index(int): "Page index."
    :param: current(bool): "If specified then show the lastest information of specified MIT. Default is not specified."
    '''
    positional = [SYMBOL]
    if trace == True: positional.append("--trace")
    if current == True: positional.append("--current")
    optional = {
        "limit": limit,
        "index": index,
    }
    return 'getmit', positional, optional


@mvs_api_v2
def getnewaccount(ACCOUNTNAME, ACCOUNTAUTH, language=None):
    '''
    :param: language(str): "Options are 'en', 'es', 'ja', 'zh_Hans', 'zh_Hant' and 'any', defaults to 'en'."
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "language": language,
    }
    return 'getnewaccount', positional, optional


@mvs_api_v2
def listmits(ACCOUNTNAME=None, ACCOUNTAUTH=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {

    }
    return 'listmits', positional, optional


@mvs_api_v2
def shutdown(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): "admin name."
    :param: ADMINAUTH(str): "admin password/authorization."
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'shutdown', positional, optional


@mvs_api_v2
def signrawtx(ACCOUNTNAME, ACCOUNTAUTH, TRANSACTION):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TRANSACTION(str): "The input Base16 transaction to sign."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TRANSACTION]

    optional = {

    }
    return 'signrawtx', positional, optional


@mvs_api_v2
def getmemorypool(json=None, ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: json(bool): "Json format or Raw format, default is Json(true)."
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {
        "json": json,
    }
    return 'getmemorypool', positional, optional


@mvs_api_v2
def getblockheader(hash=None, height=None):
    '''
    :param: hash(string of hash256): "The Base16 block hash."
    :param: height(int): "The block height."
    '''
    positional = []

    optional = {
        "hash": hash,
        "height": height,
    }
    return 'getblockheader', positional, optional


@mvs_api_v2
def listassets(ACCOUNTNAME=None, ACCOUNTAUTH=None, cert=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: cert(bool): "If specified, then only get related asset cert. Default is not specified."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]
    if cert == True: positional.append("--cert")
    optional = {

    }
    return 'listassets', positional, optional


@mvs_api_v2
def sendassetfrom(ACCOUNTNAME, ACCOUNTAUTH, FROMADDRESS, TOADDRESS, SYMBOL, AMOUNT, model=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: FROMADDRESS(str): "From address"
    :param: TOADDRESS(str): "Target address"
    :param: SYMBOL(str): "Asset symbol"
    :param: AMOUNT(int): "Asset integer bits. see asset <decimal_number>."
    :param: model(str): The token offering model by block height.
    TYPE=1 - fixed quantity model; TYPE=2 - specify parameters;
    LQ - Locked Quantity each period;
    LP - Locked Period, numeber of how many blocks;
    UN - Unlock Number, number of how many LPs;
    eg:
        TYPE=1;LQ=9000;LP=60000;UN=3
        TYPE=2;LQ=9000;LP=60000;UN=3;UC=20000,20000,20000;UQ=3000,3000,3000
    defaults to disable.
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, FROMADDRESS, TOADDRESS, SYMBOL, AMOUNT]

    optional = {
        "model": model,
        "fee": fee,
    }
    return 'sendassetfrom', positional, optional


@mvs_api_v2
def getasset(SYMBOL=None, cert=None):
    '''
    :param: SYMBOL(str): "Asset symbol. If not specified, will show whole network asset symbols."
    :param: cert(bool): "If specified, then only get related asset cert. Default is not specified."
    '''
    positional = [SYMBOL]
    if cert == True: positional.append("--cert")
    optional = {

    }
    return 'getasset', positional, optional


@mvs_api_v2
def getinfo(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'getinfo', positional, optional


@mvs_api_v2
def secondaryissue(ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, VOLUME, model=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TODID(str): "target did to check and issue asset, fee from and mychange to the address of this did too."
    :param: SYMBOL(str): "issued asset symbol"
    :param: VOLUME(int): "The volume of asset, with unit of integer bits."
    :param: model(str): The token offering model by block height.
    TYPE=1 - fixed quantity model; TYPE=2 - specify parameters;
    LQ - Locked Quantity each period;
    LP - Locked Period, numeber of how many blocks;
    UN - Unlock Number, number of how many LPs;
    eg:
        TYPE=1;LQ=9000;LP=60000;UN=3
        TYPE=2;LQ=9000;LP=60000;UN=3;UC=20000,20000,20000;UQ=3000,3000,3000
    defaults to disable.
    :param: fee(int): "The fee of tx. default_value 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, VOLUME]

    optional = {
        "model": model,
        "fee": fee,
    }
    return 'secondaryissue', positional, optional


@mvs_api_v2
def getaddressasset(ADDRESS, cert=None):
    '''
    :param: ADDRESS(str): "address"
    :param: cert(bool): "If specified, then only get related asset cert. Default is not specified."
    '''
    positional = [ADDRESS]
    if cert == True: positional.append("--cert")
    optional = {

    }
    return 'getaddressasset', positional, optional


@mvs_api_v2
def getnewaddress(ACCOUNTNAME, ACCOUNTAUTH, number=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: number(int): "The number of addresses to be generated, defaults to 1."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "number": number,
    }
    return 'getnewaddress', positional, optional


@mvs_api_v2
def getbalance(ACCOUNTNAME, ACCOUNTAUTH):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {

    }
    return 'getbalance', positional, optional


@mvs_api_v2
def getnewmultisig(ACCOUNTNAME, ACCOUNTAUTH, signaturenum, publickeynum, selfpublickey, publickey=None,
                   description=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: signaturenum(int): "Account multisig signature number."
    :param: publickeynum(int): "Account multisig public key number."
    :param: selfpublickey(str): "the public key belongs to this account."
    :param: publickey([str1, str2, ...]): "cosigner public key used for multisig"
    :param: description(str): "multisig record description."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "signaturenum": signaturenum,
        "publickeynum": publickeynum,
        "selfpublickey": selfpublickey,
        "publickey": publickey,
        "description": description,
    }
    return 'getnewmultisig', positional, optional


@mvs_api_v2
def transfermit(ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TODID(str): "Target did"
    :param: SYMBOL(str): "Asset MIT symbol"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL]

    optional = {
        "fee": fee,
    }
    return 'transfermit', positional, optional


@mvs_api_v2
def deleteaccount(ACCOUNTNAME, ACCOUNTAUTH, LASTWORD):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: LASTWORD(str): "The last word of your private-key phrase."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, LASTWORD]

    optional = {

    }
    return 'deleteaccount', positional, optional


@mvs_api_v2
def listmultisig(ACCOUNTNAME, ACCOUNTAUTH):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {

    }
    return 'listmultisig', positional, optional


@mvs_api_v2
def getdid(DidOrAddress=None):
    '''
    :param: DidOrAddress(str): "Did symbol or standard address; If no input parameters, then display whole network DIDs."
    '''
    positional = [DidOrAddress]

    optional = {

    }
    return 'getdid', positional, optional


@mvs_api_v2
def startmining(ACCOUNTNAME, ACCOUNTAUTH, address=None, number=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: address(str): "The mining target address. Defaults to empty, means a new address will be generated."
    :param: number(int): "The number of mining blocks, useful for testing. Defaults to 0, means no limit."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {
        "address": address,
        "number": number,
    }
    return 'startmining', positional, optional


@mvs_api_v2
def getwork(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'getwork', positional, optional


@mvs_api_v2
def importkeyfile(ACCOUNTNAME, ACCOUNTAUTH, FILE, FILECONTENT=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: FILE(string of file path): "key file path."
    :param: FILECONTENT(str): "key file content. this will omit the FILE argument if specified."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, FILE, FILECONTENT]

    optional = {

    }
    return 'importkeyfile', positional, optional


@mvs_api_v2
def decoderawtx(TRANSACTION):
    '''
    :param: TRANSACTION(str): "The input Base16 transaction to sign."
    '''
    positional = [TRANSACTION]

    optional = {

    }
    return 'decoderawtx', positional, optional


@mvs_api_v2
def sendasset(ACCOUNTNAME, ACCOUNTAUTH, ADDRESS, SYMBOL, AMOUNT, model=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: ADDRESS(str): "Asset receiver."
    :param: SYMBOL(str): "Asset symbol/name."
    :param: AMOUNT(int): "Asset integer bits. see asset <decimal_number>."
    :param: model(str): The token offering model by block height.
    TYPE=1 - fixed quantity model; TYPE=2 - specify parameters;
    LQ - Locked Quantity each period;
    LP - Locked Period, numeber of how many blocks;
    UN - Unlock Number, number of how many LPs;
    eg:
        TYPE=1;LQ=9000;LP=60000;UN=3
        TYPE=2;LQ=9000;LP=60000;UN=3;UC=20000,20000,20000;UQ=3000,3000,3000
    defaults to disable.
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, ADDRESS, SYMBOL, AMOUNT]

    optional = {
        "model": model,
        "fee": fee,
    }
    return 'sendasset', positional, optional


@mvs_api_v2
def submitwork(NONCE, HEADERHASH, MIXHASH):
    '''
    :param: NONCE(str): "nonce. without leading 0x"
    :param: HEADERHASH(str): "header hash. with leading 0x"
    :param: MIXHASH(str): "mix hash. with leading 0x"
    '''
    positional = [NONCE, HEADERHASH, MIXHASH]

    optional = {

    }
    return 'submitwork', positional, optional


@mvs_api_v2
def getaddressetp(PAYMENT_ADDRESS):
    '''
    :param: PAYMENT_ADDRESS(string of Base58-encoded public key address): "The payment address. If not specified the address is read from STDIN."
    '''
    positional = [PAYMENT_ADDRESS]

    optional = {

    }
    return 'getaddressetp', positional, optional


@mvs_api_v2
def gettx(HASH, json=None):
    '''
    :param: json(bool): "Json/Raw format, default is '--json=true'."
    :param: HASH(string of hash256): "The Base16 transaction hash of the transaction to get. If not specified the transaction hash is read from STDIN."
    '''
    positional = [json, HASH]

    optional = {

    }
    return 'gettx', positional, optional


@mvs_api_v2
def getmininginfo(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'getmininginfo', positional, optional


@mvs_api_v2
def registermit(ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL=None, content=None, mits=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: TODID(str): "Target did"
    :param: SYMBOL(str): "MIT symbol"
    :param: content(str): "Content of MIT"
    :param: mits([str1, str2, ...]): "List of symbol and content pair. Symbol and content are separated by a ':'"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, TODID, SYMBOL]

    optional = {
        "content": content,
        "mits": mits,
        "fee": fee,
    }
    return 'registermit', positional, optional


@mvs_api_v2
def setminingaccount(ACCOUNTNAME, ACCOUNTAUTH, PAYMENT_ADDRESS):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: PAYMENT_ADDRESS(string of Base58-encoded public key address): "the payment address of this account."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, PAYMENT_ADDRESS]

    optional = {

    }
    return 'setminingaccount', positional, optional


@mvs_api_v2
def listaddresses(ACCOUNTNAME, ACCOUNTAUTH):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH]

    optional = {

    }
    return 'listaddresses', positional, optional


@mvs_api_v2
def dumpkeyfile(ACCOUNTNAME, ACCOUNTAUTH, LASTWORD, DESTINATION=None, data=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: LASTWORD(str): "The last word of your master private-key phrase."
    :param: DESTINATION(string of file path): "The keyfile storage path to."
    :param: data(bool): "If specified, the keyfile content will be append to the report, rather than to local file specified by DESTINATION."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, LASTWORD, DESTINATION]
    if data == True: positional.append("--data")
    optional = {

    }
    return 'dumpkeyfile', positional, optional


@mvs_api_v2
def getpeerinfo(ADMINNAME=None, ADMINAUTH=None):
    '''
    :param: ADMINNAME(str): Administrator required.(when administrator_required in mvs.conf is set true)
    :param: ADMINAUTH(str): Administrator password required.
    '''
    positional = [ADMINNAME, ADMINAUTH]

    optional = {

    }
    return 'getpeerinfo', positional, optional


@mvs_api_v2
def didsendfrom(ACCOUNTNAME, ACCOUNTAUTH, FROM_, TO_, AMOUNT, memo=None, fee=None):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: FROM_(str): "Send from this did/address"
    :param: TO_(str): "Send to this did/address"
    :param: AMOUNT(int): "ETP integer bits."
    :param: memo(str): "The memo to descript transaction"
    :param: fee(int): "Transaction fee. defaults to 10000 ETP bits"
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, FROM_, TO_, AMOUNT]

    optional = {
        "memo": memo,
        "fee": fee,
    }
    return 'didsendfrom', positional, optional


@mvs_api_v2
def getaccount(ACCOUNTNAME, ACCOUNTAUTH, LASTWORD):
    '''
    :param: ACCOUNTNAME(str): Account name required.
    :param: ACCOUNTAUTH(str): Account password(authorization) required.
    :param: LASTWORD(str): "The last word of your backup words."
    '''
    positional = [ACCOUNTNAME, ACCOUNTAUTH, LASTWORD]

    optional = {

    }
    return 'getaccount', positional, optional


@mvs_api_v2
def addnode(NODEADDRESS, ADMINNAME=None, ADMINAUTH=None, operation=None):
    '''
    :param: NODEADDRESS(str): "The target node address[x.x.x.x:port]."
    :param: ADMINNAME(str): "admin name."
    :param: ADMINAUTH(str): "admin password/authorization."
    :param: operation(str): "The operation[ add|ban ] to the target node address. default: add."
    '''
    positional = [NODEADDRESS, ADMINNAME, ADMINAUTH]

    optional = {
        "operation": operation,
    }
    return 'addnode', positional, optional


@mvs_api_v2
def getblock(HASH_OR_HEIGH, json=None, tx_json=None):
    '''
    :param: HASH_OR_HEIGH(str): "block hash or block height"
    :param: json(bool): "Json/Raw format, default is '--json=true'."
    :param: tx_json(bool): "Json/Raw format for txs, default is '--tx_json=true'."
    '''
    positional = [HASH_OR_HEIGH, json, tx_json]

    optional = {

    }
    return 'getblock', positional, optional

