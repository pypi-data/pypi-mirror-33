class VeriteosException(Exception):
	def __init__(self, message, errcode):
		super(VeriteosException, self).__init__('<Response [{}]> {}'.format(errcode, message))
		self.code = errcode

		
class VeriteosInvalidRequest(VeriteosException, ValueError):
	pass
