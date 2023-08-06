from __future__ import absolute_import

from operator import itemgetter


mapping = {
    'has_header': True,
    'is_split': False,
    'delimiter': ',',
    'bank': 'BNP',
    'account': 'BNP courant',
    'date': itemgetter('Date valeur'),
    'type': 'checking',
    'amount': itemgetter('Montant'),
    'currency': itemgetter('Devise du compte'),
    'desc': itemgetter('Details'),
    'payee': itemgetter('CONTREPARTIE DE LA TRANSACTION'),
    'id': itemgetter('sequence'),
}
