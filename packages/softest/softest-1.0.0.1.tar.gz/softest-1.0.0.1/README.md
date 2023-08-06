# softest - Soft Assertions

Supports the soft assert style of testing, 
where multiple assertions can fail within the same method, 
while collecting and formatting those failures' stack traces
for reporting by a final assert_all call.
	
Such stack traces are enhanced
to include the call hierarchy
from within the test class.
	
## Usage

```
import softest

class ExampleTest(softest.SoftTestCase):
	def test_example(self):
		self.soft_assert(self.assertEqual, 'Worf', 'wharf', 'Klingon is not ship receptacle')
		self.soft_assert(self.assertTrue, True)
		self.soft_assert(self.assertTrue, False)
		
		self.assert_all()
```
