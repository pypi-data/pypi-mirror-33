import hashlib
import requests

from .veriteos_exceptions import VeriteosException, VeriteosInvalidRequest

VERITEOS_ENDPOINT = 'https://api.veriteos.com/v1'


class Client(object):

	def __init__(self, api_key, transaction_family, transaction_family_version):
		self.api_key = api_key
		self.transaction_family = transaction_family
		self.transaction_family_version = transaction_family_version


	def _sha512(self, data):
		self.data = data
		return hashlib.sha512(data).hexdigest()


	def _encode_address(self, transaction_family, address):
		self.transaction_family = transaction_family
		self.address = address
		transaction_family = self._sha512(transaction_family.encode())[0:6]
		address = self._sha512(address.encode())[0:64]
		return transaction_family + address


	def _get_request(self, endpoint, params={}):
		"""
		Makes a get request to an endpoint.

		If an error occurs, assymes that endpoint returns JSON as:
			{
				"status_code": XXX,
				"error": "error message"
			}
		"""
		r = requests.get(
				VERITEOS_ENDPOINT + endpoint,
				headers={"Content-Type": "application/json"},
				auth=(self.api_key, ''),
				params=params,
			)

		if r.status_code == 200:
			return r.json()
		else:
			try:
				error = r.json()['error']
			except ValueError:
				error = r.text
			if r.status_code == 400:
				raise VeriteosInvalidRequest(error, r.status_code)
			else:
				raise VeriteosException(error, r.status_code)


	def _post_request(self, endpoint, payload=None):
		"""
		Makes a post request to an endpoint.

		If an error occurs, assumes that endpoint returns JSON as:
			{
				"status_code": XXX,
				"error": "error message"
			}
		"""
		payload = payload or {}
		
		r = requests.post(
				VERITEOS_ENDPOINT + endpoint,
				json=payload,
				headers={"Content-Type": "application/json"},
				auth=(self.api_key, ''),
			)

		if r.ok == True:
			return r.json()
		else:
			try:
				error = r.json()['error']
			except ValueError:
				error = r.text
			if r.status_code == 400:
				raise VeriteosInvalidRequest(error, r.status_code)
			else:
				raise VeriteosException(error, r.status_code)


	def submit(self, address=None, transactions=None):
		"""
		Send list of transactions to /submit endpoint for signing
		and batching of transactions for the validator.
		"""
		self.transactions = transactions
		self.address = address
		encoded_address = self._encode_address(self.transaction_family, address)

		if type(transactions) == list:
			payload = {
				"address": encoded_address,
				"transactions": transactions,
				"transaction_family": self.transaction_family,
				"transaction_family_version": self.transaction_family_version,
			}
		else:
			raise VeriteosInvalidRequest(
				'Invalid parameters: transactions must be a list.')

		response = self._post_request(
			'/submit',
			payload=payload
		)
		return response

	# TODO: Add support for id param
	def read_batches(self, **kwargs):
		"""
		Read list of batches from /batches endpoint.
		"""
		allowed_kwargs = {'head', 'start', 'limit', 'reverse', 'id'}
		for key in kwargs:
			if key not in allowed_kwargs:
				raise VeriteosInvalidRequest('Illegal parameter %s found.' 
											 % key, None)

		response = self._get_request(
			'/batches',
			params=kwargs
		)
		return response


	def read_batch_statuses(self, **kwargs):
		"""
		Read list of batches from /batches endpoint.
		"""
		allowed_kwargs = {'id', 'wait'}
		for key in kwargs:
			if key not in allowed_kwargs:
				raise VeriteosInvalidRequest('Illegal parameter %s found.' 
											 % key, None)
		response = self._get_request(
			'/batch_statuses',
			params=kwargs
		)
		return response

	# TODO: `address` param for /state can be partial address for filtering,
	# whereas `address` param for /state/{address} has to be full address.
	def read_address(self, address=None, **kwargs):
		"""
		Read state from /state/{address} endpoint.
		"""
		self.address = address
		allowed_kwargs = {'head'}
		for key in kwargs:
			if key not in allowed_kwargs:
				raise VeriteosInvalidRequest('Illegal parameter %s found.' 
											 % key, None)
		encoded_address = self._encode_address(self.transaction_family, address)
		response = self._get_request(
			'/state/{}'.format(encoded_address),
			params=kwargs
		)
		return response

	# TODO: incomplete method
	def read_state(self, **kwargs):
		"""
		Read state from /state endpoint.
		"""
		allowed_kwargs = {'head', 'address', 'start', 'limit', 'reverse'}
		for key in kwargs:
			if key not in allowed_kwargs:
				raise VeriteosInvalidRequest('Illegal parameter %s found.' 
											 % key, None)
		response = self._get_request(
			'/state',
			params=kwargs
		)
		return response


	# TODO: incomplete method
	def read_blocks(self, block_id=None, **kwargs):
		"""
		Read list of blocks from /blocks endpoint.
		"""
		self.block_id = block_id
		allowed_kwargs = {'head', 'start', 'limit', 'reverse'}
		for key in kwargs:
			if key not in allowed_kwargs:
				raise VeriteosInvalidRequest('Illegal parameter %s found.' 
											 % key, None)
		response = self._get_request(
			'/blocks{}'.format('/' + block_id),
			params=kwargs
		)
		return response

	# TODO: incomplete method
	def read_transactions(self, id=[], **kwargs):
		"""
		Read list of blocks from /transactions endpoint.
		"""
		self.block_id = block_id
		allowed_kwargs = {'head', 'start', 'limit', 'reverse'}
		for key in kwargs:
			if key not in allowed_kwargs:
				raise VeriteosInvalidRequest('Illegal parameter %s found.' 
											 % key, None)
		response = self._get_request(
			'/transactions{}'.format('/' + block_id),
			params=kwargs
		)
		return response

	# TODO: incomplete method
	def read_receipts(self, transaction_ids=[]):
		"""
		Read receipts for list of transactions from /receipts endpoint.
		"""
		response = self._get_request(
			'/receipts',
			params=kwargs
		)
		return response


	def read_peers(self):
		"""
		Read peers from /peers endpoint.
		"""
		response = self._get_request('/peers')
		return response
