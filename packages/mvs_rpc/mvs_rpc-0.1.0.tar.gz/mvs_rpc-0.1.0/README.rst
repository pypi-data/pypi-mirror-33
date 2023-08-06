<p align="center">
  <a href="https://www.myetpwallet.com/">
    <img src="https://mvs.org/images/metaverselogo.png" alt="">
  </a>
</p>

Metaverse Python SDK
=========================
This is a python implemention of mvs rpc client.
All functions are named by mvs api method, you can easily find the method introduction from:
https://docs.mvs.org/api_v2/

Installation:
```
$ pip install mvs_rpc
```

Usage:
```
>>> from mvs_rpc import mvs_api
>>> errmsg, result = mvs_api.getblockheader()
>>> print errmsg
None
>>> print result
{u'nonce': u'7787652087139548244', u'hash': u'13ba9b153d5ef1191f60b37533d8e1c4761fd27d214d4fb46d7275644b6d341f', u'bits': u'10', u'previous_block_hash': u'4f5899c22ad5e2d32d783c73484b58aca8cc3d694d753719f353baf19e0b7af8', u'number': 4402, u'transaction_count': 1, u'version': 1, u'mixhash': u'98368172253342782875271646966540868150764974751689304684446442086367385278', u'time_stamp': 1530248902, u'merkle_tree_hash': u'9969cd405dc237e6a3a799c01e516670825d35120fc2f88a3cb292be1229b07a'}

```
