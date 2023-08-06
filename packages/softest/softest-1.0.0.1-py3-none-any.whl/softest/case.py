"""Soft test case implementation"""

import os
import sys
import traceback
import unittest

from typing import Tuple


class TestCase(unittest.TestCase):
	"""
	Supports the soft assert style of testing, 
	where multiple assertions can fail within the same method, 
	while collecting and formatting those failures' stack traces
	for reporting by a final assert_all call.
	
	Such stack traces are enhanced
	to include the call hierarchy
	from within the test class.
	
	@see: soft_assert
	@see: assert_all
	@usage:	
		import softest
	
		class ExampleTest(softest.TestCase):
			def test_example(self):
				self.soft_assert(self.assertEqual, 'Worf', 'wharf', 'Klingon is not ship receptacle')
				self.soft_assert(self.assertTrue, True)
				self.soft_assert(self.assertTrue, False)
		
				self.assert_all()
		
		
		if __name__ == '__main__':
			softest.main()
	"""

	__UNIT_TEST_CASE_MODULE_FILE_PATH = 'unittest' + os.sep + 'case.py'
	_asserted_exceptions = []


	def __init__(self, methodName:str = 'runTest'):
		unittest.TestCase.__init__(self, methodName);


	def __get_module_and_class_names(self) -> str:
		if self.__class__.__module__ == "__main__":
			return '({})'.format(self.__class__.__qualname__)
		else:
			return '({}.{})'.format(self.__class__.__module__, self.__class__.__qualname__)


	def __str__(self):
		return '"{}" {}'.format(self._testMethodName, self.__get_module_and_class_names())


	def __get_stack_and_first_test_class_frame_index(self) -> Tuple[list, int]:
		"""
		Extracts the stack,
		then searches it 
		for the first frame of the test class.
		
		@return: [0] the extracted stack
			[1] the frame index
		"""
		frames = traceback.extract_stack()
		target_index = -1;
		frame_file_path = ''

		while(not frame_file_path.endswith(self.__UNIT_TEST_CASE_MODULE_FILE_PATH)):
			target_index -= 1;
			frame_file_path = frames[target_index].filename;

		return frames, target_index + 1


	def soft_assert(self, assert_method, *arguments, **keywords):
		"""
		Asserts the specified comparison 
		and stores any raised AssertionErrors stack traces 
		for later reporting.
		
		@param assert_method: the method definition for the desired assert call 
		@see: assert_all
		"""
		try:
			assert_method(*arguments, **keywords)
		except AssertionError as ae:
			# collect all relevant code traces to combine for extra details in the log
			formatted_frames = traceback.format_exception(AssertionError, ae, sys.exc_info()[2])
			frames, target_index = self.__get_stack_and_first_test_class_frame_index()

			# skipping the SoftTestCase calls to keep focused on the test class
			test_class_frames = frames[target_index:-2]
			test_class_frames = traceback.format_list(test_class_frames)

			for frame in test_class_frames:
				formatted_frames.insert(1, frame)

			self._asserted_exceptions.append(formatted_frames)


	def assert_all(self, method_name:str = None):
		"""
		Prints all collected assertion exceptions,
		then clears the collection,
		and finally fails the method.
		
		@param: method_name: overrides the auto-detection of the caller's displayed function name when specified
		@see: self.fail 
		"""
		if not method_name:
			frames, target_index = self.__get_stack_and_first_test_class_frame_index()
			method_name = frames[target_index].name
			full_signature = '"{}" {}'.format(method_name, self.__get_module_and_class_names())
		else:
			full_signature = str(self)

		if self._asserted_exceptions:
			print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

			count = len(self._asserted_exceptions)

			failures_found = ['The following']
			failures_found.append(str(count) + ' failures were' if count > 1 else 'failure was')
			failures_found.append('found in {}:'.format(full_signature))

			print(' '.join(failures_found))
			print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

			for index, failure in enumerate(self._asserted_exceptions):
				if count > 1:
					if index > 0:
						print('+--------------------------------------------------------------------+')

					print('Failure {} ("{}" method)'.format(index + 1, method_name))
					print('+--------------------------------------------------------------------+')

				print(''.join(failure) + '')

			self._asserted_exceptions.clear()

			if count > 1:
				failure_message = '{} had {} failures, as printed to the console'.format(full_signature, count)
			else:
				failure_message = '{} had 1 failure, as printed to the console'.format(full_signature)

			self.fail(failure_message)
